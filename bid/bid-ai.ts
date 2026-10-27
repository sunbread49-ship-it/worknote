// Supabase Edge Function "bid-ai" v4 — 규격대조 페이지의 프롬프트(와 카탈로그 페이지 이미지)를 Google Gemini(무료 등급)에 전달하고 답을 돌려준다.
// 두 가지 방식으로 불린다:
//   1) 브라우저가 직접 호출 (집 등 일반 네트워크)
//   2) 회사 네트워크 우회: 브라우저가 bid_jobs 표에 작업을 쓰면, DB 트리거가 서버 안에서 { job_id } 로 호출 → 결과를 표에 기록
// 필요한 Secrets: GEMINI_API_KEY (aistudio.google.com 무료 키), ALLOWED_EMAILS(쉼표로 구분, 이 이메일로 로그인한 사람만 사용 가능)
import { createClient } from "npm:@supabase/supabase-js@2";

declare const EdgeRuntime: { waitUntil(p: Promise<unknown>): void } | undefined;

// 쓸 수 있는 무료 모델. 페이지가 순서를 정해 보낼 수 있고, 앞 모델이 한도에 걸리면 다음 모델로 넘어간다.
const ALLOWED_MODELS = ["gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.5-flash-lite"];
const DEFAULT_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"];
const LEVELS = ["minimal", "low", "medium", "high"];
const IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "application/pdf"];
const MAX_IMAGE_CHARS = 18_000_000; // base64 합계 상한(약 13MB)
const BUDGET_MS = 140000; // Supabase 무료 플랜 150초 제한 안에서 끝낸다

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

const URL_ = Deno.env.get("SUPABASE_URL")!;
const allowedEmail = (email?: string | null) =>
  (Deno.env.get("ALLOWED_EMAILS") || "").split(",").map((s) => s.trim().toLowerCase()).filter(Boolean).includes((email || "").toLowerCase());

type Part = { text: string } | { inlineData: { mimeType: string; data: string } };
type AskBody = { prompt?: string; models?: string[]; thinking?: string; images?: { mime?: string; data?: string }[] };

async function askGemini(model: string, key: string, parts: Part[], level: string | null, ms: number) {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), ms);
  try {
    const generationConfig: Record<string, unknown> = { responseMimeType: "application/json", maxOutputTokens: 32768 };
    if (level) generationConfig.thinkingConfig = { thinkingLevel: level };
    const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
      method: "POST",
      signal: ctl.signal,
      headers: { "Content-Type": "application/json", "x-goog-api-key": key },
      body: JSON.stringify({ contents: [{ role: "user", parts }], generationConfig }),
    });
    const body = await r.json().catch(() => ({}));
    return { status: r.status, body };
  } catch (e) {
    return { status: (e as Error)?.name === "AbortError" ? 504 : 0, body: { error: { message: String(e) } } };
  } finally {
    clearTimeout(timer);
  }
}

// 요청 하나를 처리해서 [HTTP 상태, 응답 본문]을 돌려준다
async function run(body: AskBody, t0: number): Promise<[number, Record<string, unknown>]> {
  const key = Deno.env.get("GEMINI_API_KEY");
  if (!key) return [500, { error: "no_api_key" }];
  const prompt = String(body.prompt || "");
  if (!prompt) return [400, { error: "bad_request" }];
  const asked = (Array.isArray(body.models) ? body.models : []).filter((m) => ALLOWED_MODELS.includes(m));
  const models = asked.length ? asked : DEFAULT_MODELS;
  const level = LEVELS.includes(String(body.thinking)) ? String(body.thinking) : "low";

  const parts: Part[] = [];
  let imageChars = 0;
  for (const im of Array.isArray(body.images) ? body.images : []) {
    const mime = String(im?.mime || ""), data = String(im?.data || "");
    if (!IMAGE_TYPES.includes(mime) || !data) continue;
    imageChars += data.length;
    if (imageChars > MAX_IMAGE_CHARS) return [413, { error: "too_large" }];
    parts.push({ inlineData: { mimeType: mime, data } });
  }
  parts.push({ text: prompt });

  const tried: { model: string; status: number; sec: number; note?: string }[] = [];
  let last = { status: 0, body: {} as any };
  for (const model of models) {
    const left = BUDGET_MS - (Date.now() - t0);
    if (left < 15000) break;
    const t1 = Date.now();
    last = await askGemini(model, key, parts, level, left);
    if (last.status === 400 && /thinking/i.test(String(last.body?.error?.message || ""))) {
      last = await askGemini(model, key, parts, null, BUDGET_MS - (Date.now() - t0));
    }
    const { status, body: b } = last;
    tried.push({ model, status, sec: Math.round((Date.now() - t1) / 1000), note: String(b?.error?.message || "").slice(0, 120) || undefined });
    if (status === 200) {
      if (b.promptFeedback?.blockReason) return [422, { error: "refused", tried }];
      const cand = b.candidates?.[0];
      const text = (cand?.content?.parts || []).filter((p: any) => !p.thought && typeof p.text === "string").map((p: any) => p.text).join("");
      if (!text) { if (cand?.finishReason === "SAFETY") return [422, { error: "refused", tried }]; continue; }
      return [200, { text, model, finish: cand?.finishReason, sec: Math.round((Date.now() - t0) / 1000), tried }];
    }
    const msg = String(b?.error?.message || "");
    if (status === 400 && /api key/i.test(msg)) return [500, { error: "bad_api_key", tried }];
    if (status === 403) return [500, { error: "bad_api_key", message: msg, tried }];
    // 429(한도), 404(모델 없음), 504(시간 초과), 5xx(일시 오류)는 다음 모델로
  }
  if (last.status === 429) return [429, { error: "rate_limited", tried }];
  if (last.status === 504) return [504, { error: "timeout", tried }];
  return [502, { error: "upstream_error", status: last.status, message: String(last.body?.error?.message || ""), tried }];
}

// 회사 네트워크 우회: 표에 쓰인 작업을 처리하고 결과를 표에 기록한다
async function runJob(jobId: string) {
  const admin = createClient(URL_, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
  const { data: job } = await admin.from("bid_jobs").select("id,user_id,status,request").eq("id", jobId).single();
  if (!job || job.status !== "queued") return;
  const { data: u } = await admin.auth.admin.getUserById(job.user_id);
  if (!allowedEmail(u?.user?.email)) {
    await admin.from("bid_jobs").update({ status: "error", error: "not_allowed", updated_at: new Date().toISOString() }).eq("id", jobId);
    return;
  }
  await admin.from("bid_jobs").update({ status: "running", updated_at: new Date().toISOString() }).eq("id", jobId);
  let st = 500, out: Record<string, unknown> = { error: "upstream_error" };
  try { [st, out] = await run(job.request || {}, Date.now()); } catch (e) { out = { error: "upstream_error", message: String(e) }; }
  await admin.from("bid_jobs").update(
    st === 200
      ? { status: "done", result: out, request: {}, updated_at: new Date().toISOString() }
      : { status: "error", error: String(out.error || "upstream_error"), result: out, request: {}, updated_at: new Date().toISOString() },
  ).eq("id", jobId);
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: "method_not_allowed" }, 405);
  const t0 = Date.now();

  let body: AskBody & { job_id?: string };
  try { body = await req.json(); } catch { return json({ error: "bad_request" }, 400); }

  // 2) DB 트리거가 보낸 작업 — 바로 답하고 뒤에서 처리
  if (body.job_id) {
    const task = runJob(String(body.job_id));
    if (typeof EdgeRuntime !== "undefined") { EdgeRuntime.waitUntil(task); return json({ accepted: true }, 202); }
    await task; return json({ done: true });
  }

  // 1) 브라우저 직접 호출 — 로그인한 본인인지 확인
  const token = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  const sb = createClient(URL_, Deno.env.get("SUPABASE_ANON_KEY")!);
  const { data: { user } } = await sb.auth.getUser(token);
  if (!user) return json({ error: "not_signed_in" }, 401);
  if (!allowedEmail(user.email)) return json({ error: "not_allowed" }, 403);
  const [st, out] = await run(body, t0);
  return json(out, st);
});

// Supabase Edge Function "bid-ai" v2 — 규격대조 페이지가 보낸 프롬프트를 Google Gemini(무료 등급)에 전달하고 답을 돌려준다.
// 필요한 Secrets: GEMINI_API_KEY (aistudio.google.com 무료 키), ALLOWED_EMAILS(쉼표로 구분, 이 이메일로 로그인한 사람만 사용 가능)
import { createClient } from "npm:@supabase/supabase-js@2";

// 쓸 수 있는 무료 모델. 페이지가 순서를 정해 보낼 수 있고, 앞 모델이 한도에 걸리면 다음 모델로 넘어간다.
const ALLOWED_MODELS = ["gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.5-flash-lite"];
const DEFAULT_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"];
const LEVELS = ["minimal", "low", "medium", "high"];
const BUDGET_MS = 140000; // Supabase 무료 플랜 150초 제한 안에서 끝낸다

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

async function askGemini(model: string, key: string, prompt: string, level: string | null, ms: number) {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), ms);
  try {
    const generationConfig: Record<string, unknown> = { responseMimeType: "application/json", maxOutputTokens: 32768 };
    if (level) generationConfig.thinkingConfig = { thinkingLevel: level };
    const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
      method: "POST",
      signal: ctl.signal,
      headers: { "Content-Type": "application/json", "x-goog-api-key": key },
      body: JSON.stringify({ contents: [{ role: "user", parts: [{ text: prompt }] }], generationConfig }),
    });
    const body = await r.json().catch(() => ({}));
    return { status: r.status, body };
  } catch (e) {
    return { status: (e as Error)?.name === "AbortError" ? 504 : 0, body: { error: { message: String(e) } } };
  } finally {
    clearTimeout(timer);
  }
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: "method_not_allowed" }, 405);
  const t0 = Date.now();

  // 로그인한 본인인지 확인
  const token = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_ANON_KEY")!);
  const { data: { user } } = await sb.auth.getUser(token);
  if (!user) return json({ error: "not_signed_in" }, 401);
  const allowed = (Deno.env.get("ALLOWED_EMAILS") || "").split(",").map((s) => s.trim().toLowerCase()).filter(Boolean);
  if (!allowed.includes((user.email || "").toLowerCase())) return json({ error: "not_allowed" }, 403);
  const key = Deno.env.get("GEMINI_API_KEY");
  if (!key) return json({ error: "no_api_key" }, 500);

  let body: { prompt?: string; models?: string[]; thinking?: string };
  try { body = await req.json(); } catch { return json({ error: "bad_request" }, 400); }
  const prompt = String(body.prompt || "");
  if (!prompt) return json({ error: "bad_request" }, 400);
  const asked = (Array.isArray(body.models) ? body.models : []).filter((m) => ALLOWED_MODELS.includes(m));
  const models = asked.length ? asked : DEFAULT_MODELS;
  const level = LEVELS.includes(String(body.thinking)) ? String(body.thinking) : "low";

  const tried: { model: string; status: number; sec: number; note?: string }[] = [];
  let last = { status: 0, body: {} as any };
  for (const model of models) {
    const left = BUDGET_MS - (Date.now() - t0);
    if (left < 15000) break;
    const t1 = Date.now();
    last = await askGemini(model, key, prompt, level, left);
    // 이 모델이 생각 단계 설정을 모르면 설정 없이 한 번 더
    if (last.status === 400 && /thinking/i.test(String(last.body?.error?.message || ""))) {
      last = await askGemini(model, key, prompt, null, BUDGET_MS - (Date.now() - t0));
    }
    const { status, body: b } = last;
    tried.push({ model, status, sec: Math.round((Date.now() - t1) / 1000), note: String(b?.error?.message || "").slice(0, 120) || undefined });
    if (status === 200) {
      if (b.promptFeedback?.blockReason) return json({ error: "refused", tried }, 422);
      const cand = b.candidates?.[0];
      const text = (cand?.content?.parts || []).filter((p: any) => !p.thought && typeof p.text === "string").map((p: any) => p.text).join("");
      if (!text) { if (cand?.finishReason === "SAFETY") return json({ error: "refused", tried }, 422); continue; }
      return json({ text, model, finish: cand?.finishReason, sec: Math.round((Date.now() - t0) / 1000), tried });
    }
    const msg = String(b?.error?.message || "");
    if (status === 400 && /api key/i.test(msg)) return json({ error: "bad_api_key", tried }, 500);
    if (status === 403) return json({ error: "bad_api_key", message: msg, tried }, 500);
    // 429(한도), 404(모델 없음), 504(시간 초과), 5xx(일시 오류)는 다음 모델로
  }
  if (last.status === 429) return json({ error: "rate_limited", tried }, 429);
  if (last.status === 504) return json({ error: "timeout", tried }, 504);
  return json({ error: "upstream_error", status: last.status, message: String(last.body?.error?.message || ""), tried }, 502);
});

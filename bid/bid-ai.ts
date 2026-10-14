// Supabase Edge Function "bid-ai" — 규격대조 페이지가 보낸 프롬프트를 Claude에 전달하고 답을 돌려준다.
// 필요한 Secrets: ANTHROPIC_API_KEY, ALLOWED_EMAILS(쉼표로 구분, 이 이메일로 로그인한 사람만 사용 가능)
import Anthropic from "npm:@anthropic-ai/sdk";
import { createClient } from "npm:@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

const anthropic = new Anthropic({ apiKey: Deno.env.get("ANTHROPIC_API_KEY") });

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: "method_not_allowed" }, 405);

  // 로그인한 본인인지 확인
  const token = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_ANON_KEY")!);
  const { data: { user } } = await sb.auth.getUser(token);
  if (!user) return json({ error: "not_signed_in" }, 401);
  const allowed = (Deno.env.get("ALLOWED_EMAILS") || "").split(",").map((s) => s.trim().toLowerCase()).filter(Boolean);
  if (!allowed.includes((user.email || "").toLowerCase())) return json({ error: "not_allowed" }, 403);
  if (!Deno.env.get("ANTHROPIC_API_KEY")) return json({ error: "no_api_key" }, 500);

  let body: { prompt?: string; effort?: string };
  try { body = await req.json(); } catch { return json({ error: "bad_request" }, 400); }
  const prompt = String(body.prompt || "");
  if (!prompt) return json({ error: "bad_request" }, 400);
  const effort = ["low", "medium", "high"].includes(String(body.effort)) ? String(body.effort) : "medium";

  try {
    const msg = await anthropic.beta.messages.stream({
      model: "claude-opus-5",
      max_tokens: 32000,
      thinking: { type: "adaptive" },
      output_config: { effort },
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
      messages: [{ role: "user", content: prompt }],
    } as any).finalMessage();

    if (msg.stop_reason === "refusal") return json({ error: "refused" }, 422);
    const text = msg.content.filter((b: any) => b.type === "text").map((b: any) => b.text).join("");
    return json({ text, stop_reason: msg.stop_reason, usage: msg.usage });
  } catch (e) {
    if (e instanceof Anthropic.RateLimitError) return json({ error: "rate_limited" }, 429);
    if (e instanceof Anthropic.AuthenticationError) return json({ error: "bad_api_key" }, 500);
    if (e instanceof Anthropic.APIError) return json({ error: "upstream_error", status: e.status, message: e.message }, 502);
    return json({ error: "upstream_error", message: String(e) }, 502);
  }
});

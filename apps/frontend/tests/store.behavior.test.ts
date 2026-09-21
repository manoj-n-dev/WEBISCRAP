// Behavioural test for the chat store (no framework needed):  npx tsx tests/store.behavior.test.ts
// Covers: client-generated session id, no dataset clobbering, follow-up mode, Groq-limit error, attachments, logout/account-switch reset.
import assert from "node:assert/strict";
import { useChatStore, chatHasDataset } from "../src/lib/store/chat";
import { ApiClient } from "../src/lib/api/client";

type Call = { url: string; method: string; body?: any };
const calls: Call[] = [];
let chatResponder: (body: any) => { status: number; json: any } = () => ({ status: 200, json: {} });

(globalThis as any).fetch = async (url: string, init: any = {}) => {
  const body = init.body && typeof init.body === "string" ? JSON.parse(init.body) : init.body;
  calls.push({ url: String(url), method: init.method || "GET", body });
  const u = String(url);
  let r: { status: number; json: any };
  if (u.includes("/api/chat/") && (init.method === "POST") && u.endsWith("/api/chat/")) r = chatResponder(body);
  else if (u.includes("/history")) r = { status: 200, json: { history: [{ role: "user", content: "hi" }, { role: "assistant", content: "hello" }] } };
  else if (u.includes("/data")) r = { status: 200, json: { cleaned_data: [{ a: 1 }, { a: 2 }], total_rows: 2, validation: { confidence_score: 88 } } };
  else if (u.endsWith("/api/chat/sessions")) r = { status: 200, json: { sessions: [{ id: "s1", title: "First", timestamp: 1 }] } };
  else if (u.includes("/api/upload/")) r = { status: 200, json: { kind: "table", rows: 3 } };
  else r = { status: 200, json: {} };
  return new Response(JSON.stringify(r.json), { status: r.status, headers: { "content-type": "application/json" } });
};

const S = () => useChatStore.getState();
const uuidRe = /^[0-9a-f-]{36}$/;
(async () => {
  // 1. first message in a NEW chat: session id is generated client-side and sent
  chatResponder = (b) => ({ status: 200, json: { status: "success", session_id: b.session_id, data: { mode: "extraction", completed_steps: ["plan","extract","clean","validate"], cleaned_data: [{ n: "A" }], dataset_rows: 1, dataset_cols: 1, validation: { confidence_score: 91, validation_notes: "ok" }, conversation_response: { response_text: "Extracted 1 row" } } } });
  const p = S().submitExtraction("get products https://ex.com", "https://ex.com");
  assert.ok(S().activeSessionId && uuidRe.test(S().activeSessionId!), "client generates the session id BEFORE the request");
  assert.equal(S().isPipelineActive, true);
  assert.equal(S().messages[1].status, "running"); assert.equal(S().messages[1].mode, "extraction");
  await p;
  const post = calls.find((c) => c.method === "POST" && c.url.endsWith("/api/chat/"))!;
  assert.equal(post.body.session_id, S().activeSessionId, "same id sent to the server");
  assert.equal(S().messages[1].status, "completed"); assert.equal(S().messages[1].confidenceScore, 91);
  assert.equal(S().messages[1].data?.length, 1);
  assert.ok(chatHasDataset(S().messages));
  console.log("1 ok  new chat: id generated client-side, response applied");

  // 2. redirect remount must NOT wipe the data (FE-01)
  const sid = S().activeSessionId!; const before = S().messages.length;
  S().setActiveSession(sid);
  await new Promise((r) => setTimeout(r, 30));
  assert.equal(S().messages.length, before); assert.ok(S().messages[1].data, "data card survives setActiveSession");
  assert.equal(calls.filter((c) => c.url.includes("/history")).length, 0, "no history refetch for a loaded chat");
  console.log("2 ok  setActiveSession keeps the loaded chat (dataset card not cleared)");

  // 3. follow-up: no URL, dataset exists -> followup mode, no pipeline strip state
  chatResponder = (b) => ({ status: 200, json: { status: "success", data: { mode: "followup", cleaned_data: [{ n: "A" }], dataset_rows: 1, result_rows: [{ n: "A" }], conversation_response: { response_text: "Cheapest is A", result_count: 1 }, export_url: "/api/export/csv?session_id=x" } } });
  const f = S().submitExtraction("which is cheapest?", "");
  assert.equal(S().messages.at(-1)!.mode, "followup", "follow-up detected on the client");
  await f;
  const last = S().messages.at(-1)!;
  assert.equal(last.data, undefined, "no dataset card for follow-ups"); assert.equal(last.confidenceScore, undefined);
  assert.equal(last.resultRows?.length, 1); assert.equal(last.exportUrl, "/api/export/csv?session_id=x");
  console.log("3 ok  follow-up: mode=followup, no data/quality card, result rows + export link kept");

  // 4. Groq limit -> structured error, no crash
  chatResponder = () => ({ status: 429, json: { detail: { code: "LLM_RATE_LIMIT", message: "limit", retry_after: 33, scope: "minute" } } });
  await S().submitExtraction("again", "");
  const e = S().messages.at(-1)!;
  assert.equal(e.status, "error"); assert.equal(e.error?.code, "LLM_RATE_LIMIT"); assert.equal(e.error?.retryAfter, 33); assert.equal(e.error?.scope, "minute");
  assert.equal(S().isPipelineActive, false);
  console.log("4 ok  429 LLM_RATE_LIMIT surfaces code + retryAfter (drives the limit panel)");

  // 5. attachments: new chat -> uploads go to a client id; chips ready; consumed on send
  S().startNewChat();
  assert.equal(S().activeSessionId, null);
  await S().addAttachments([new File(["a,b\n1,2\n"], "sales.csv"), new File(["x"], "evil.exe")]);
  const up = calls.filter((c) => c.url.includes("/api/upload/")).at(-1)!;
  assert.ok(up.url.includes("session_id=" + S().activeSessionId), "upload attached to the chat session id");
  assert.equal(S().pendingAttachments[0].status, "ready"); assert.equal(S().pendingAttachments[0].rows, 3);
  assert.equal(S().pendingAttachments[1].status, "error");
  chatResponder = (b) => ({ status: 200, json: { status: "success", data: { mode: "extraction", cleaned_data: [{ a: 1 }], dataset_rows: 1, conversation_response: { response_text: "Loaded" } } } });
  await S().submitExtraction("", "");
  assert.equal(S().messages[0].attachments?.length, 1); assert.match(S().messages[0].content, /sales\.csv/);
  assert.equal(S().pendingAttachments.length, 0);
  console.log("5 ok  attachments: chips, client session id on upload, message carries the file, chips cleared");

  // 6. identity switch drops chats but keeps the server-scoped session list; resetAll wipes everything
  await S().loadSessions(); assert.equal(S().sessions.length, 1);
  S().bindUser("userA"); S().bindUser("userB");
  assert.equal(S().messages.length, 0); assert.equal(S().sessions.length, 1);
  S().resetAll(); assert.equal(S().sessions.length, 0); assert.equal(S().userId, null);
  console.log("6 ok  bindUser/resetAll: no stale chats after account switch or logout");

  // 7. history hydration re-attaches dataset preview
  S().setActiveSession("11111111-2222-4333-8444-555555555555");
  await new Promise((r) => setTimeout(r, 60));
  const m = S().messages; assert.equal(m.length, 2); assert.equal(m[1].data?.length, 2); assert.equal(m[1].confidenceScore, 88);
  console.log("7 ok  reopening a chat restores text AND the dataset preview");
  console.log("ALL STORE CHECKS PASSED");
})().catch((e) => { console.error("FAIL", e); process.exit(1); });

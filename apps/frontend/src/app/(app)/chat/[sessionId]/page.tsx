import React from "react";
import ChatView from "@/components/chat/ChatView";

// The page is only a shell (all data is fetched client-side with the user's token), so it can be prerendered and
// served from the CDN. "new" is built at deploy time; other ids are generated once on first request and then cached.
export const dynamicParams = true;
export function generateStaticParams() {
  return [{ sessionId: "new" }];
}

export default async function ChatPage({ params }: { params: Promise<{ sessionId: string }> }) {
  const { sessionId } = await params;
  return <ChatView routeId={sessionId} />;
}

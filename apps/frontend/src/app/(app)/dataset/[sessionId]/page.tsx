import React from "react";
import DatasetView from "@/components/dataset/DatasetView";

export const dynamicParams = true;
export function generateStaticParams() {
  return [];
}

export default async function DatasetPage({ params }: { params: Promise<{ sessionId: string }> }) {
  const { sessionId } = await params;
  return <DatasetView sessionId={sessionId} />;
}

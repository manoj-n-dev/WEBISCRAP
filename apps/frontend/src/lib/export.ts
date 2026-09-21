import { ApiClient } from "@/lib/api/client";

export type ExportFormat = "csv" | "excel" | "json" | "md" | "pdf";

/** Readable text for any cell value (never "[object Object]" / "undefined"). */
export function formatCell(v: unknown): string {
  if (v === null || v === undefined) return "";
  if (Array.isArray(v)) return v.map((x) => (typeof x === "object" && x !== null ? JSON.stringify(x) : String(x))).join("; ");
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

/** Union of keys across ALL rows (LLM-extracted rows often differ), first-seen order. */
export function columnsOf(rows: Record<string, unknown>[]): string[] {
  const seen = new Set<string>();
  rows.forEach((r) => Object.keys(r).forEach((k) => seen.add(k)));
  return Array.from(seen);
}

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

/** jsPDF + autotable (~130 KB gzip) are loaded ONLY when someone actually exports a PDF. */
export async function downloadPDF(data: Record<string, unknown>[], filename = "webiscrap_export") {
  if (!data.length) return;
  const [{ default: jsPDF }, { default: autoTable }] = await Promise.all([import("jspdf"), import("jspdf-autotable")]);
  const headers = columnsOf(data);
  const doc = new jsPDF({ orientation: headers.length > 5 ? "landscape" : "portrait" });
  doc.setFontSize(16);
  doc.text("WEBISCRAP - Extracted Data", 14, 18);
  doc.setFontSize(10);
  doc.setTextColor(100);
  doc.text(`${data.length} rows exported on ${new Date().toLocaleDateString()}`, 14, 26);
  autoTable(doc, {
    startY: 32,
    head: [headers],
    body: data.map((row) => headers.map((h) => formatCell(row[h]))),
    theme: "striped",
    styles: { fontSize: 8, cellPadding: 3 },
    headStyles: { fillColor: [20, 119, 245], textColor: 255 },
  });
  doc.save(`${filename}.pdf`);
}

/**
 * Export a session's FULL dataset. CSV / Excel(.xlsx) / JSON / Markdown are produced by the backend
 * (correct extension, UTF-8 BOM, real .xlsx, nested values flattened). PDF is rendered in the browser.
 */
export async function exportSession(format: ExportFormat, sessionId: string): Promise<void> {
  if (format === "pdf") {
    const res = await ApiClient.getSessionData(sessionId);
    const rows = (res?.cleaned_data || []) as Record<string, unknown>[];
    if (!rows.length) throw new Error("There is no data to export yet.");
    await downloadPDF(rows);
    return;
  }
  await ApiClient.downloadExport(sessionId, format === "md" ? "markdown" : format);
}

/** Offline fallback (no session id): CSV with BOM + union columns, or JSON. */
export function exportRows(format: "csv" | "json", data: Record<string, unknown>[], filename = "webiscrap_export") {
  if (!data.length) return;
  if (format === "json") {
    triggerDownload(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }), `${filename}.json`);
    return;
  }
  const headers = columnsOf(data);
  const esc = (s: string) => `"${s.replace(/"/g, '""')}"`;
  const lines = [headers.map(esc).join(","), ...data.map((r) => headers.map((h) => esc(formatCell(r[h]))).join(","))];
  triggerDownload(new Blob(["\uFEFF" + lines.join("\r\n")], { type: "text/csv;charset=utf-8" }), `${filename}.csv`);
}

import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

// C7: Formula injection protection — prefix dangerous leading chars with a single quote
const FORMULA_CHARS = new Set(["=", "+", "-", "@", "\t", "\r", "\n"]);
function sanitizeCellValue(val: string): string {
  if (val.length > 0 && FORMULA_CHARS.has(val[0])) {
    return "'" + val;
  }
  return val;
}

export function downloadJSON(data: Record<string, any>[], filename = "webiscrap_export") {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: "application/json" });
  triggerDownload(blob, `${filename}.json`);
}

export function downloadCSV(data: Record<string, any>[], filename = "webiscrap_export") {
  if (!data.length) return;
  const headers = Object.keys(data[0]);
  const csvRows = [
    headers.join(","),
    ...data.map((row) =>
      headers.map((h) => {
        const val = sanitizeCellValue(String(row[h] ?? "")).replace(/"/g, '""');
        return `"${val}"`;
      }).join(",")
    ),
  ];
  const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8;" });
  triggerDownload(blob, `${filename}.csv`);
}

export function downloadExcel(data: Record<string, any>[], filename = "webiscrap_export") {
  // Excel can open CSV files natively. We use tab-separated values with .xls extension
  // for better Excel compatibility without requiring heavy xlsx libraries.
  if (!data.length) return;
  const headers = Object.keys(data[0]);
  const tsvRows = [
    headers.join("\t"),
    ...data.map((row) =>
      headers.map((h) => sanitizeCellValue(String(row[h] ?? "")).replace(/\t/g, " ")).join("\t")
    ),
  ];
  const blob = new Blob(["\uFEFF" + tsvRows.join("\n")], {
    type: "application/vnd.ms-excel;charset=utf-8;",
  });
  triggerDownload(blob, `${filename}.xls`);
}

export function downloadMarkdown(data: Record<string, any>[], filename = "webiscrap_export") {
  if (!data.length) return;
  const headers = Object.keys(data[0]);
  const headerRow = `| ${headers.join(" | ")} |`;
  const separator = `| ${headers.map(() => "---").join(" | ")} |`;
  const bodyRows = data.map(
    (row) => `| ${headers.map((h) => sanitizeCellValue(String(row[h] ?? ""))).join(" | ")} |`
  );
  const md = [headerRow, separator, ...bodyRows].join("\n");
  const blob = new Blob([md], { type: "text/markdown;charset=utf-8;" });
  triggerDownload(blob, `${filename}.md`);
}

export function downloadPDF(data: Record<string, any>[], filename = "webiscrap_export") {
  if (!data.length) return;
  const headers = Object.keys(data[0]);

  const doc = new jsPDF({ orientation: headers.length > 5 ? "landscape" : "portrait" });

  // Title
  doc.setFontSize(16);
  doc.text("WEBISCRAP - Extracted Data", 14, 18);
  doc.setFontSize(10);
  doc.setTextColor(100);
  doc.text(`${data.length} rows exported on ${new Date().toLocaleDateString()}`, 14, 26);

  // Table
  autoTable(doc, {
    startY: 32,
    head: [headers],
    body: data.map((row) => headers.map((h) => sanitizeCellValue(String(row[h] ?? "")))),
    theme: "striped",
    styles: { fontSize: 8, cellPadding: 3 },
    headStyles: { fillColor: [20, 119, 245], textColor: 255 },
  });

  doc.save(`${filename}.pdf`);
}

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function exportData(
  format: "csv" | "excel" | "json" | "md" | "pdf",
  data: Record<string, any>[],
  filename = "webiscrap_export"
) {
  switch (format) {
    case "csv":
      downloadCSV(data, filename);
      break;
    case "excel":
      downloadExcel(data, filename);
      break;
    case "json":
      downloadJSON(data, filename);
      break;
    case "md":
      downloadMarkdown(data, filename);
      break;
    case "pdf":
      downloadPDF(data, filename);
      break;
  }
}

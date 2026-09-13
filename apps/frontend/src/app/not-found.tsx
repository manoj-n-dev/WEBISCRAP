import Link from "next/link";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-0 px-6">
      {/* Subtle radial background glow */}
      <div
        className="pointer-events-none fixed inset-0"
        aria-hidden="true"
        style={{
          background:
            "radial-gradient(ellipse 60% 40% at 50% 20%, rgba(20,119,245,0.08) 0%, transparent 70%)",
        }}
      />

      <Card className="relative z-10 w-full max-w-md text-center rounded-2xl p-1">
        <CardHeader className="pb-2">
          {/* Status badge */}
          <span className="inline-block mx-auto mb-4 px-3 py-1 rounded-full border border-glass-border-strong bg-white/5 font-mono text-[11px] text-signal-400 uppercase tracking-[0.08em]">
            404 · Page not found
          </span>

          <CardTitle className="text-[28px] font-display font-semibold text-text-hi">
            Nothing here.
          </CardTitle>
        </CardHeader>

        <CardContent className="flex flex-col items-center gap-6">
          <CardDescription className="text-[14px] text-text-dim leading-relaxed max-w-[280px]">
            The page you&apos;re looking for doesn&apos;t exist or has been
            moved. Head back to the home page to start a new extraction.
          </CardDescription>

          <Button variant="primary" asChild>
            <Link href="/">Back to home</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

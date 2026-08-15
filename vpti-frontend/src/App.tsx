import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ModeToggle } from "@/components/mode-toggle"

// Halaman verifikasi token desain VPTI — bukan halaman produk final,
// hanya membuktikan bahwa @theme inline + shadcn + dark mode bekerja.

const STAGES = [
  { label: "Registrasi", status: "selesai" as const },
  { label: "Verifikasi Dokumen", status: "selesai" as const },
  { label: "Inspeksi Lapangan", status: "berjalan" as const },
  { label: "Review Hasil", status: "menunggu" as const },
  { label: "Rilis LS", status: "menunggu" as const },
]

function statusVariant(status: string) {
  if (status === "selesai") return "success" as const
  if (status === "berjalan") return "warning" as const
  return "outline" as const
}

function App() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border">
        <div className="max-w-3xl mx-auto flex items-center justify-between px-6 py-4">
          <div>
            <div className="text-sm font-semibold text-primary">VPTI Design System</div>
            <div className="text-xs text-muted-foreground">Verifikasi token — Tailwind v4 + shadcn/ui</div>
          </div>
          <ModeToggle />
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Contoh Permohonan — LS-2026-1003</CardTitle>
            <CardDescription>Kaca Pangan · Diajukan 12 Agu 2026</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {STAGES.map(s => (
              <div key={s.label} className="flex items-center justify-between text-sm">
                <span className="text-foreground">{s.label}</span>
                <Badge variant={statusVariant(s.status)}>{s.status}</Badge>
              </div>
            ))}
            <div className="flex flex-wrap gap-2 pt-2">
              <Button>Setujui &amp; Teruskan</Button>
              <Button variant="outline">Kembalikan</Button>
              <Button variant="destructive">Tolak</Button>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <Card><CardContent className="pt-4"><div className="text-2xl font-semibold">6</div><div className="text-xs text-muted-foreground">Total Permohonan</div></CardContent></Card>
          <Card><CardContent className="pt-4"><div className="text-2xl font-semibold text-accent-foreground">2</div><div className="text-xs text-muted-foreground">Perlu Tindakan</div></CardContent></Card>
          <Card><CardContent className="pt-4"><div className="text-2xl font-semibold text-success">2</div><div className="text-xs text-muted-foreground">LS Terbit</div></CardContent></Card>
        </div>
      </main>
    </div>
  )
}

export default App

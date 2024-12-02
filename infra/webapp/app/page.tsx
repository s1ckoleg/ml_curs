import Form from "@/components/form";
import { Button } from "@/components/ui/button";
import { GITHUB_URL, PRESENTATION_URL } from "@/lib/const";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col gap-8 items-center justify-center w-full h-screen font-[family-name:var(--font-geist-mono)] relative">
      <main className="w-full flex flex-col flex-1 items-center justify-center gap-4">
        <Form />
      </main>
      <footer className="flex flex-row gap-4 text-center justify-center pb-4 w-full">
        <p>
          <Button variant="link" asChild>
            <Link href={GITHUB_URL} target="_blank">
              GitHub
            </Link>
          </Button>
          <Button asChild variant="link">
            <Link href={PRESENTATION_URL} target="_blank">
              Presentation
            </Link>
          </Button>
        </p>
      </footer>
    </div>
  );
}

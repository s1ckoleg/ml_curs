import Form from "@/components/form";

export default function Home() {
  return (
    <div className="flex flex-col gap-8 items-center justify-center w-full h-screen font-[family-name:var(--font-geist-mono)]">
      <main className="max-w-lg w-full flex flex-col gap-4">
        <Form />
      </main>
    </div>
  );
}

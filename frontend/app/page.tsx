import ChatWindow from "@/components/views/ChatWindow"

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto max-w-4xl h-screen flex flex-col">
        {/* Header */}
        <header className="flex items-center justify-center py-8 border-b border-white/10">
          <h1 className="text-3xl font-bold gradient-text">Ask Taylor </h1>
        </header>

        {/* Chat Interface */}
        <div className="flex-1 flex flex-col">
          <ChatWindow />
        </div>
      </div>
    </main>
  )
}

"use client"

// View: Message input component
import { useState, type KeyboardEvent } from "react"
import { Button } from "@/components/ui/button"
import { Send } from "lucide-react"

interface ChatInputProps {
  onSendMessage: (message: string) => void
}

export default function ChatInput({ onSendMessage }: ChatInputProps) {
  const [message, setMessage] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!message.trim() || isSubmitting) return

    setIsSubmitting(true)
    const messageToSend = message
    setMessage("")

    try {
      await onSendMessage(messageToSend)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="flex items-end space-x-3">
      <div className="flex-1">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
          className="
            w-full px-4 py-3 glass-input rounded-2xl
            resize-none focus:outline-none
            text-sm leading-relaxed min-h-[48px] max-h-32
            placeholder:text-gray-400 text-white
          "
          rows={1}
          disabled={isSubmitting}
        />
      </div>

      <Button
        onClick={handleSubmit}
        disabled={!message.trim() || isSubmitting}
        size="lg"
        className="px-4 py-3 h-12 glass-emerald text-white border-0 hover-glow disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Send className="w-4 h-4" />
        <span className="sr-only">Send message</span>
      </Button>
    </div>
  )
}

"use client"

// View: Main chat interface component
import { useState, useEffect, useRef } from "react"
import { ChatController } from "../controllers/ChatController"
import type { Message } from "../models/ChatModel"
import ChatMessage from "./ChatMessage"
import ChatInput from "./ChatInput"

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([])
  const [controller] = useState(() => new ChatController(setMessages))
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Initialize with welcome message
  useEffect(() => {
    const timer = setTimeout(() => {
      controller.sendMessage("Hello! Welcome to our chat system.")
    }, 500)

    return () => clearTimeout(timer)
  }, [controller])

  const handleSendMessage = async (content: string) => {
    await controller.sendMessage(content)
  }

  const handleClearChat = () => {
    controller.clearChat()
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-400">
              <div className="w-20 h-20 mx-auto mb-6 glass-grey rounded-full flex items-center justify-center text-3xl">
                💬
              </div>
              <p className="text-lg font-medium text-white mb-2">Start a conversation</p>
              <p className="text-sm">Type a message below to begin chatting with our AI assistant</p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Chat Input Area */}
      <div className="glass-grey border-t border-white/10 p-6">
        <ChatInput onSendMessage={handleSendMessage} />

        {/* Clear Chat Button */}
        {messages.length > 0 && (
          <div className="flex justify-center mt-4">
            <button
              onClick={handleClearChat}
              className="text-xs text-gray-400 hover:text-emerald-400 transition-all duration-300 hover:scale-105"
            >
              Clear conversation
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

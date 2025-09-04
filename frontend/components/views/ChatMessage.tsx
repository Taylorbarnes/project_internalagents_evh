// View: Individual message bubble component
import type { Message } from "../models/ChatModel"

interface ChatMessageProps {
  message: Message
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.sender === "user"
  const isLoading = message.isLoading

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} message-fade-in`}>
      <div className={`max-w-[80%] ${isUser ? "order-2" : "order-1"}`}>
        {/* Message Bubble */}
        <div
          className={`
            px-4 py-3 rounded-2xl text-sm leading-relaxed transition-all duration-300
            ${isUser ? "glass-emerald text-white ml-auto hover-glow" : "glass-grey text-gray-300 border-0 hover-glow"}
            ${isLoading ? "animate-pulse" : ""}
          `}
        >
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce"></div>
              </div>
              <span className="text-emerald-300 text-xs">Thinking...</span>
            </div>
          ) : (
            <p className="text-pretty">{message.content}</p>
          )}
        </div>

        {/* Timestamp */}
        {!isLoading && (
          <div className={`text-xs text-gray-400 mt-2 ${isUser ? "text-right" : "text-left"}`}>
            {message.timestamp.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        )}
      </div>

      {/* Avatar */}
      <div className={`flex-shrink-0 ${isUser ? "order-1 mr-3" : "order-2 ml-3"}`}>
        <div
          className={`
          w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium
          backdrop-filter backdrop-blur-md border border-white/20 transition-all duration-300 hover-glow
          ${isUser ? "glass-emerald text-white" : "glass-grey text-gray-300"}
        `}
        >
          {isUser ? "👤" : "🤖"}
        </div>
      </div>
    </div>
  )
}

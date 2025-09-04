// Model: Data structures and business logic
export interface Message {
  id: string
  content: string
  sender: "user" | "agent"
  timestamp: Date
  isLoading?: boolean
}

export interface Agent {
  id: string
  name: string
  avatar: string
  description: string
  isActive: boolean
}

export class ChatModel {
  private messages: Message[] = []
  private currentAgent: Agent = {
    id: "default",
    name: "Assistant",
    avatar: "🤖",
    description: "Your helpful AI assistant",
    isActive: true,
  }

  // Mock API responses
  private mockResponses = [
    "Hello! I'm your AI assistant. How can I help you today?",
    "That's an interesting question. Let me think about that...",
    "I understand what you're asking. Here's what I think:",
    "Thanks for sharing that with me. I'd be happy to help!",
    "That's a great point. Let me provide some insights on that.",
    "I see what you mean. Here's my perspective on this topic:",
  ]

  getMessages(): Message[] {
    return [...this.messages]
  }

  addMessage(content: string, sender: "user" | "agent"): Message {
    const message: Message = {
      id: Date.now().toString(),
      content,
      sender,
      timestamp: new Date(),
    }

    this.messages.push(message)
    return message
  }

  addLoadingMessage(): Message {
    const loadingMessage: Message = {
      id: `loading-${Date.now()}`,
      content: "",
      sender: "agent",
      timestamp: new Date(),
      isLoading: true,
    }

    this.messages.push(loadingMessage)
    return loadingMessage
  }

  removeLoadingMessage(messageId: string): void {
    this.messages = this.messages.filter((msg) => msg.id !== messageId)
  }

  // Mock API call simulation
  async generateResponse(): Promise<string> {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 2000))

    // Return random mock response
    const randomIndex = Math.floor(Math.random() * this.mockResponses.length)
    return this.mockResponses[randomIndex]
  }

  getCurrentAgent(): Agent {
    return this.currentAgent
  }

  clearMessages(): void {
    this.messages = []
  }
}

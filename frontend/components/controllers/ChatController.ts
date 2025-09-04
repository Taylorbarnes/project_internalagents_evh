// Controller: Orchestrates interactions between Model and View
import { ChatModel, type Message } from "../models/ChatModel"

export class ChatController {
  private model: ChatModel
  private onMessagesUpdate: (messages: Message[]) => void

  constructor(onMessagesUpdate: (messages: Message[]) => void) {
    this.model = new ChatModel()
    this.onMessagesUpdate = onMessagesUpdate
  }

  async sendMessage(content: string): Promise<void> {
    if (!content.trim()) return

    try {
      // Add user message
      this.model.addMessage(content.trim(), "user")
      this.notifyUpdate()

      // Add loading indicator
      const loadingMessage = this.model.addLoadingMessage()
      this.notifyUpdate()

      // Generate agent response (mock API call)
      const response = await this.model.generateResponse()

      // Remove loading indicator
      this.model.removeLoadingMessage(loadingMessage.id)

      // Add agent response
      this.model.addMessage(response, "agent")
      this.notifyUpdate()
    } catch (error) {
      console.error("Error sending message:", error)

      // Remove loading indicator on error
      const messages = this.model.getMessages()
      const loadingMsg = messages.find((msg) => msg.isLoading)
      if (loadingMsg) {
        this.model.removeLoadingMessage(loadingMsg.id)
      }

      // Add error message
      this.model.addMessage("Sorry, I encountered an error. Please try again.", "agent")
      this.notifyUpdate()
    }
  }

  getMessages(): Message[] {
    return this.model.getMessages()
  }

  clearChat(): void {
    this.model.clearMessages()
    this.notifyUpdate()
  }

  private notifyUpdate(): void {
    this.onMessagesUpdate(this.model.getMessages())
  }

  // Future: This is where we'll integrate with real backend API
  // async callBackendAPI(message: string): Promise<string> {
  //   const response = await fetch('/api/chat', {
  //     method: 'POST',
  //     headers: { 'Content-Type': 'application/json' },
  //     body: JSON.stringify({ message, agentId: this.model.getCurrentAgent().id })
  //   })
  //   const data = await response.json()
  //   return data.response
  // }
}

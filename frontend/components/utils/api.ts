// Utility: API helper functions for future backend integration

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
}

export interface ChatRequest {
  message: string
  agentId?: string
  conversationId?: string
}

export interface ChatResponse {
  response: string
  agentId: string
  conversationId: string
}

// Future API integration helper
export class ApiClient {
  private baseUrl: string

  constructor(baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:5000") {
    this.baseUrl = baseUrl.replace(/\/$/, "")
  }

  async sendChatMessage(request: ChatRequest): Promise<ApiResponse<ChatResponse>> {
    try {
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return { success: true, data }
    } catch (error) {
      console.error("API Error:", error)
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error occurred",
      }
    }
  }

  async getAgents(): Promise<ApiResponse<any[]>> {
    try {
      const response = await fetch(`${this.baseUrl}/agents`)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return { success: true, data }
    } catch (error) {
      console.error("API Error:", error)
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error occurred",
      }
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient()

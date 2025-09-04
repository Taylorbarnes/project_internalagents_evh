# Chatbot MVC App

A modern, scalable chatbot interface built with React, Next.js, and TailwindCSS following Model-View-Controller (MVC) architecture principles.

## Features

- 🎨 **Modern UI**: Clean, ChatGPT-inspired interface with semantic design tokens
- 🏗️ **MVC Architecture**: Proper separation of concerns for scalability
- 💬 **Real-time Chat**: Smooth messaging experience with loading indicators
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile
- 🔌 **API Ready**: Structured for easy backend integration
- 🐳 **Containerized**: Docker support for easy deployment
- ♿ **Accessible**: WCAG compliant with proper ARIA labels

## Architecture

### Model (`/components/models/`)
- `ChatModel.ts`: Data structures and business logic
- Handles message storage, agent management, and mock API responses

### View (`/components/views/`)
- `ChatWindow.tsx`: Main chat interface container
- `ChatMessage.tsx`: Individual message bubble component
- `ChatInput.tsx`: Message input with send functionality

### Controller (`/components/controllers/`)
- `ChatController.ts`: Orchestrates Model-View interactions
- Manages message flow and API communication

### Utils (`/components/utils/`)
- `api.ts`: API client helpers for future backend integration

## Getting Started

### Development
\`\`\`bash
npm install
npm run dev
\`\`\`

### Production Build
\`\`\`bash
npm run build
npm start
\`\`\`

### Docker Deployment
\`\`\`bash
docker build -t chatbot-app .
docker run -p 3000:3000 chatbot-app
\`\`\`

## Future Enhancements

- **Backend Integration**: Replace mock responses with real API calls
- **Multiple Agents**: Support for different AI agents with unique personalities
- **Message History**: Persistent conversation storage
- **File Uploads**: Support for image and document sharing
- **Real-time Updates**: WebSocket integration for live responses

## API Integration

The app is structured to easily integrate with a backend API. Update the `ChatController` to use the `ApiClient` class:

\`\`\`typescript
// Replace mock API call in ChatController.ts
const response = await apiClient.sendChatMessage({
  message: content,
  agentId: this.model.getCurrentAgent().id
});
\`\`\`

## Design System

The app uses semantic design tokens defined in `globals.css` for consistent theming:
- Primary: Rose-600 (#be123c)
- Secondary: Pink-500 (#ec4899)  
- Neutrals: Slate color palette
- Supports both light and dark modes

## Contributing

1. Follow the MVC pattern when adding new features
2. Use semantic design tokens from `globals.css`
3. Maintain TypeScript strict mode compliance
4. Add proper accessibility attributes for new components

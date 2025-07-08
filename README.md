# Temp Project

This is a FastAPI application that provides a chat assistant with file upload and session management.

## Features

- Chat with an AI assistant
- Upload files and ask questions about their content
- Manage chat sessions (create, clear, retrieve history)

## API Endpoints

-   `POST /api/chat`: Send a chat message and get a response from the AI assistant.
-   `POST /api/upload`: Upload a file and ask a question about its content.
-   `POST /api/sessions/new`: Create a new chat session.
-   `GET /api/sessions/{session_id}/history`: Get the chat history for a specific session.
-   `POST /api/sessions/{session_id}/clear`: Clear the chat history for a specific session.
-   `GET /api/sessions/{session_id}/info`: Get information about a specific session.
-   `GET /health`: Health check endpoint.

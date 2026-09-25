# Real-Time Chat API

A real-time chat backend built with FastAPI, PostgreSQL and WebSockets.

The project provides user authentication, conversations, messaging and real-time message delivery through WebSockets.

## Features

* User registration and authentication
* Password hashing with Argon2
* JWT access and refresh tokens
* Protected API endpoints
* Create conversations with multiple users
* Add members to conversations
* Send and retrieve messages
* Delete own messages
* WebSocket real-time messaging
* Conversation membership validation
* Pydantic request/response validation
* Async database operations
* Alembic database migrations
* Unit tests with pytest
* Dockerized PostgreSQL

## Tech Stack

* Python 3.10+
* FastAPI
* SQLAlchemy 2.0
* PostgreSQL
* AsyncPG
* Alembic
* Pydantic
* Pydantic Settings
* PyJWT
* pwdlib + Argon2
* WebSockets
* pytest
* Docker
* uv

## Project Structure

```text
realtime-chat/
├── alembic/
│   └── versions/
├── src/
│   └── chat/
│       ├── models/
│       ├── repositories/
│       ├── routes/
│       ├── schemas/
│       ├── services/
│       ├── websocket/
│       ├── config.py
│       ├── database.py
│       ├── security.py
│       └── main.py
├── tests/
├── .env.example
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── README.md
```

## Architecture

The project uses a layered architecture:

```text
Routes
   ↓
Services
   ↓
Repositories
   ↓
PostgreSQL
```

WebSocket connections are managed separately:

```text
Client
   ↓
WebSocket endpoint
   ↓
ConnectionManager
   ↓
MessageService
   ↓
MessageRepository
   ↓
PostgreSQL
```

The service layer contains business logic, while repositories are responsible for database operations.

## Database Models

The application uses four main tables:

* `users` — registered users
* `conversations` — chat conversations
* `conversation_members` — users participating in conversations
* `messages` — messages sent in conversations

A message belongs to a conversation and has a sender.

Deleting a user does not delete conversation history. If the sender is deleted, the message remains in the database and its `sender_id` can become `NULL`.

## Authentication

Authentication uses JWT tokens.

### Login

The login endpoint uses OAuth2 password flow:

```text
POST /auth/login
```

The response contains an access token and refresh token.

Protected HTTP endpoints use:

```text
Authorization: Bearer <access_token>
```

WebSocket authentication is performed using the token in the query string:

```text
ws://127.0.0.1:8000/ws/{conversation_id}?token=<access_token>
```

Only users who are members of the conversation can establish a WebSocket connection.

## API

### Authentication

```text
POST /auth/register
POST /auth/login
POST /auth/refresh
```

### Conversations

```text
POST /conversations/
GET  /conversations/{conversation_id}
GET  /conversations/user/{user_id}
POST /conversations/{conversation_id}/members/{user_id}
```

### Messages

```text
POST   /messages/?conversation_id={conversation_id}
GET    /messages/{message_id}
GET    /messages/conversation/{conversation_id}
DELETE /messages/{message_id}
```

### WebSocket

```text
WS /ws/{conversation_id}?token={access_token}
```

When a client sends a message through WebSocket, the message is:

1. Validated with Pydantic.
2. Checked for conversation membership.
3. Saved to PostgreSQL.
4. Broadcast to all connected clients in the conversation.

Example WebSocket message:

```json
{
  "content": "Hello!"
}
```

Example response:

```json
{
  "id": 1,
  "conversation_id": 1,
  "sender_id": 1,
  "content": "Hello!",
  "created_at": "2026-09-25T07:57:00.771607+00:00"
}
```

## Installation

### 1. Clone the repository

```bash
git clone <https://github.com/alexx5039-bot/realtime-chat.git>
cd realtime-chat
```

### 2. Install dependencies

The project uses `uv`.

```bash
uv sync
```

### 3. Configure environment variables

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

Configure PostgreSQL and JWT settings in `.env`.

Example:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=realtime_chat

JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

Do not commit `.env` to Git.

### 4. Start PostgreSQL

```bash
docker compose up -d
```

### 5. Run migrations

```bash
uv run alembic upgrade head
```

### 6. Start the application

```bash
uv run uvicorn chat.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Running Tests

Run all tests:

```bash
uv run pytest -v
```

The tests cover the main service and WebSocket scenarios, including:

* successful message creation
* conversation and membership validation
* message retrieval
* message deletion permissions
* WebSocket connection
* WebSocket message sending
* WebSocket membership validation

## WebSocket Testing

A simple HTML WebSocket client can be used to test real-time communication between multiple browser tabs.

Connect using:

```text
ws://127.0.0.1:8000/ws/{conversation_id}?token={access_token}
```

Open the client in two browser tabs and connect both users to the same conversation.

When one user sends a message, the message is persisted in PostgreSQL and broadcast to the connected clients.

## Database Migrations

Create a migration after changing models:

```bash
uv run alembic revision --autogenerate -m "Describe changes"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

## Development

The project follows a simple layered structure:

* **Routes** — HTTP/WebSocket endpoints
* **Schemas** — request and response validation
* **Services** — business logic
* **Repositories** — database operations
* **Models** — SQLAlchemy database models
* **WebSocket manager** — active WebSocket connection management

The application uses asynchronous database access with SQLAlchemy and asyncpg.

## License

This project was created as a learning and portfolio project.

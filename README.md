# AI PDF Chat Platform with MCP

Upload a text-based PDF and chat with its content. Built with a React frontend, a FastAPI backend, PostgreSQL + pgvector, Google Gemini, and a small local MCP server that provides a word-definition tool. Everything runs through Docker Compose.

## Features

- Sign up, email OTP verification (Gmail SMTP), login with JWT
- View and update profile, change password, forgot and reset password with an email OTP
- Upload one or more PDFs, list them, delete them, view chat history per PDF
- Chat with a selected PDF. Answers use only the PDF content. If the answer is not in the PDF, the bot says: "I could not find this information in the selected document."
- MCP tool `get_word_definition(word)`: asking "What does authentication mean?" makes the LLM call the tool

## Architecture

How a question is answered:
1. The question is embedded with Gemini.
2. pgvector returns the 5 closest chunks of the selected PDF (filtered by the logged-in user).
3. The chunks and question go to Gemini with the rule "answer only from this text".
4. If the user asks for a word's meaning, Gemini calls the MCP tool over HTTP and uses the result.
5. The question and answer are saved in the database.

## Requirements

- Docker Desktop (with Docker Compose)
- A Gmail account with 2-Step Verification and a Gmail App Password
- A Gemini API key from https://aistudio.google.com

## Setup

1. Copy the example environment file and fill in your values:
```bash
   cp .env.example .env        # Windows PowerShell: copy .env.example .env
```
   Set `POSTGRES_PASSWORD`, `JWT_SECRET`, `SMTP_USER`, `SMTP_APP_PASSWORD` (16 characters, no spaces) and `GEMINI_API_KEY`.
2. Start everything:
```bash
   docker compose up --build
```
3. Open the app:
   - Frontend: http://localhost:5173
   - API docs: http://localhost:8000/docs
   - MCP server: http://localhost:8001 (internal use)

Never commit `.env`. It is listed in `.gitignore`.

## Using the app

1. Create an account and enter the OTP sent to your email.
2. Log in, open My PDFs, and upload a text-based PDF.
3. Click Chat and ask questions about the PDF.
4. Ask "What does authentication mean?" to see the MCP tool in action. The answer shows "Dictionary tool used for: authentication".

## Testing the MCP tool directly

```bash
docker compose exec backend python -c "from app.mcp_client import get_word_definition; print(get_word_definition('authentication'))"
docker compose logs mcp --tail 10
```

## API overview

| Area | Endpoints |
|---|---|
| Auth | `POST /auth/signup`, `/auth/verify-email`, `/auth/resend-otp`, `/auth/login`, `/auth/forgot-password`, `/auth/reset-password` |
| Users (JWT) | `GET /users/me`, `PUT /users/me`, `POST /users/change-password` |
| Documents (JWT) | `POST /documents/upload`, `GET /documents`, `DELETE /documents/{id}` |
| Chat (JWT) | `POST /chat/ask`, `GET /chat/history/{document_id}` |

## Project structure

## Notes and limitations

- Only text-based PDFs are supported (no OCR). Maximum 15 MB per file.
- The API uploads one PDF per request. The React page uploads several PDFs one after another.
- Access tokens last 60 minutes. Logging out removes the token in the browser.
- The model name is set with `GEMINI_CHAT_MODEL`. Change it in `.env` if Google retires a model.

## Troubleshooting

- No OTP email: check Spam, confirm `SMTP_USER` and `SMTP_APP_PASSWORD` in `.env`, then run `docker compose up -d --force-recreate backend`.
- Chat returns an error: run `docker compose logs backend --tail 30`.
- Changed `.env`: restart with `docker compose up -d --force-recreate backend`.
# Database schema

PostgreSQL 16 with the pgvector extension. Tables are created automatically on backend startup.

```mermaid
erDiagram
    USERS ||--o{ EMAIL_OTPS : has
    USERS ||--o{ PASSWORD_RESET_OTPS : has
    USERS ||--o{ DOCUMENTS : uploads
    USERS ||--o{ CHUNKS : owns
    USERS ||--o{ CHAT_MESSAGES : writes
    DOCUMENTS ||--o{ CHUNKS : "split into"
    DOCUMENTS ||--o{ CHAT_MESSAGES : "discussed in"

    USERS {
        int id PK
        string name
        string email UK
        string password_hash
        bool is_verified
        datetime created_at
    }
    EMAIL_OTPS {
        int id PK
        int user_id FK
        string otp_hash
        datetime expires_at
        bool used
        datetime created_at
    }
    PASSWORD_RESET_OTPS {
        int id PK
        int user_id FK
        string otp_hash
        datetime expires_at
        bool used
        datetime created_at
    }
    DOCUMENTS {
        int id PK
        int user_id FK
        string filename
        int num_chunks
        datetime created_at
    }
    CHUNKS {
        int id PK
        int document_id FK
        int user_id FK
        int chunk_index
        text content
        vector_768 embedding
    }
    CHAT_MESSAGES {
        int id PK
        int user_id FK
        int document_id FK
        text question
        text answer
        datetime created_at
    }
    REVOKED_TOKENS {
        int id PK
        string jti UK
        datetime expires_at
    }
```

Notes:
- Passwords are stored as bcrypt hashes. OTPs are stored as SHA-256 hashes, expire after 10 minutes, and can be used once.
- All foreign keys use `ON DELETE CASCADE`: deleting a user removes their PDFs, chunks, chats and OTPs, and deleting a PDF removes its chunks and chat messages.
- Every chunk and chat message stores `user_id`, and every query filters on it, so users can only reach their own PDFs.
- `embedding` is a 768-dimension pgvector column searched with cosine distance.
- `revoked_tokens` stores the IDs of JWTs that were logged out, so they stop working immediately. It has no foreign key.
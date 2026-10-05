from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_APP_PASSWORD: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_CHAT_MODEL: str = "gemini-flash-latest"
    GEMINI_FALLBACK_MODEL: str = "gemini-flash-lite-latest"
    MCP_SERVER_URL: str = "http://mcp:8001"
    OTP_EXPIRE_MINUTES: int = 10

settings = Settings()
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"

    class Config:
        env_file = ".env"

settings = Settings()

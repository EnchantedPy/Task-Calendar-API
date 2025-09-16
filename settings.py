from pydantic import BaseModel

class Settings(BaseModel):
    HOST: str = "localhost"
    PORT: int = 5432
    DB: str = "postgres"
    USER: str = "postgres"
    PASSWD: str = "passwd"

    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.USER}:{self.PASSWD}@{self.HOST}:{self.PORT}/{self.DB}"

settings = Settings()
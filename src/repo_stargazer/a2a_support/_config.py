from pydantic import BaseModel


class AgentServerConfig(BaseModel):
    host: str = "localhost"
    port: int = 10001

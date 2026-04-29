from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(_:FastAPI):
    app = FastAPI(
        title = "Todo API",
        description = "API para gerenciamento de tarefas com arquitetura em camadas.",
        version = "1.0.0",
        lifespan = lifespan, contact = {
            "name:" "Equipe da disciplina INF8B",
        },)
    return app
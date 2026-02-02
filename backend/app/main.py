from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers import threads, chat

load_dotenv()

app = FastAPI(title="RAG App API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(threads.router)
app.include_router(chat.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

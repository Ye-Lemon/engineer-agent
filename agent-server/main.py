from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from crud.user import create_tables
from router.user import router as auth_router
from router.file import router as file_router
from router.task import router as task_router
from utils.exception_handles import register_exception_handlers
from router.rag import router as rag_router

app = FastAPI(title="Engineering Agent API")
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173",
                   "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup() -> None:
    try:
        await create_tables()
    except Exception:
        # API and in-memory RAG remain usable when MySQL is not running locally.
        pass

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(file_router)
app.include_router(task_router)
app.include_router(rag_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

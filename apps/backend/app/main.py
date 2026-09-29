from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from .api.routes import router
from .core.config import get_settings

app = FastAPI(title="Интерактивный статистический атлас Казахстана", version="0.1.0", default_response_class=ORJSONResponse)
app.add_middleware(CORSMiddleware, allow_origins=get_settings().cors, allow_methods=["GET"], allow_headers=["*"])
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}


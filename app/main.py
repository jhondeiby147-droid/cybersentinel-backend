from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.db import database

app = FastAPI(title="CyberSentinel AI API")

# Configuración de CORS
origins = [
    "http://localhost:4200", # URL por defecto de Angular
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "CyberSentinel AI Backend Running"}

# Incluimos las rutas con un prefijo para ordenarlas mejor
app.include_router(api_router, prefix="/api/v1", tags=["Análisis"])


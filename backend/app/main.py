from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import auth, admin, aprendiz, instructor

app = FastAPI(
    title="API Evaluación Instructores SENA",
    description="Sistema de evaluación de instructores",
    version="1.0.0"
)

# Permitir que React se conecte (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos (fotos de instructores, etc.)
# app/static -> se crea automáticamente la primera vez que se sube una foto
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Incluir las rutas
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administración"])
app.include_router(aprendiz.router, prefix="/api/aprendiz", tags=["Aprendiz"])
app.include_router(instructor.router, prefix="/api/instructor", tags=["Instructor"])

@app.get("/")
def root():
    return {"mensaje": "API Evaluación Instructores SENA funcionando correctamente"}
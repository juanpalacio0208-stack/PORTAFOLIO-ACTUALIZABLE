"""Servidor independiente HU-17; se puede integrar en backend/main.py más adelante."""

from fastapi import FastAPI

from .router import router

app = FastAPI(title="Importaciones Euroamericanas — HU-17", version="0.1.0")
app.include_router(router)


@app.get("/", tags=["Estado"])
def inicio():
    return {"mensaje": "Catálogo mayorista disponible", "hu": "HU-17", "ruta": "/mayoristas"}

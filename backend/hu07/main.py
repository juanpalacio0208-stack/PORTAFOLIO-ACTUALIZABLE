"""HU-07: cambio de disponibilidad. Entorno local sin login."""
from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
from . import repository as repo
from .schemas import Disponibilidad
app = FastAPI(title='Importaciones Euroamericanas - HU-07')
BASE = Path(__file__).resolve().parent

@app.get('/admin/disponibilidad',include_in_schema=False)
def interfaz(): return FileResponse(BASE/'panel.html')

@app.get('/catalogo',include_in_schema=False)
def catalogo(): return FileResponse(BASE/'catalogo.html')

@app.get('/api/hu07/productos')
def listar(): return repo.leer()

@app.get('/api/hu07/catalogo')
def catalogo_publico(): return [p for p in repo.leer() if p.get('disponible') is True]

@app.patch('/api/hu07/productos/{producto_id}/disponibilidad')
def cambiar(producto_id:int,entrada:Disponibilidad):
    with repo.bloqueo():
        productos=repo.leer()
        p=repo.buscar(productos,producto_id)
        if p is None: raise HTTPException(404,'Producto no encontrado')
        p['disponible']=entrada.disponible
        repo.guardar(productos)
    return p

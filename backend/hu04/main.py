"""HU-04: registro de productos. Entorno de desarrollo local sin login."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from . import repository as repo
from .schemas import ProductoNuevo
app = FastAPI(title='Importaciones Euroamericanas - HU-04')
BASE = Path(__file__).resolve().parent

@app.get('/admin/agregar-producto',include_in_schema=False)
def interfaz(): return FileResponse(BASE/'panel.html')

@app.get('/api/hu04/productos')
def listar(): return repo.leer()

@app.post('/api/hu04/productos',status_code=201)
def crear(entrada: ProductoNuevo):
    with repo.bloqueo():
        productos=repo.leer()
        identificador=max((p.get('id',0) for p in productos),default=0)+1
        p={'id':identificador,**entrada.model_dump(exclude_none=True)}
        productos.append(p)
        repo.guardar(productos)
    return p

@app.get('/catalogo',include_in_schema=False)
def catalogo(): return FileResponse(BASE/'catalogo.html')

@app.get('/api/hu04/catalogo')
def catalogo_publico(): return [p for p in repo.leer() if p.get('disponible') is True]

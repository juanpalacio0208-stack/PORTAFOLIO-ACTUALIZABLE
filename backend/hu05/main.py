"""HU-05: edición de productos. Entorno local de demostración sin login."""
from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
from . import repository as repo
from .schemas import DatosProducto
app = FastAPI(title='Importaciones Euroamericanas - HU-05')
BASE = Path(__file__).resolve().parent

@app.get('/admin/editar-producto',include_in_schema=False)
def interfaz(): return FileResponse(BASE/'panel.html')

@app.get('/api/hu05/productos')
def listar(): return repo.leer()

@app.put('/api/hu05/productos/{producto_id}')
def editar(producto_id:int,entrada:DatosProducto):
    with repo.bloqueo():
        productos=repo.leer()
        producto=repo.buscar(productos,producto_id)
        if producto is None: raise HTTPException(404,'Producto no encontrado')
        producto.update(entrada.model_dump())
        repo.guardar(productos)
    return producto

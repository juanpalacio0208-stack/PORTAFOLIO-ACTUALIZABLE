# HU-17 — Consultar catálogo mayorista

**Épica:** Consulta del portafolio.

> Como cliente mayorista, quiero consultar un catálogo de productos para compra al por mayor, para conocer precios y condiciones de compra en volumen.

## Criterios de aceptación cubiertos

1. El cliente mayorista accede a un catálogo específico en `GET /mayoristas`.
2. Se muestran únicamente los productos con `disponible: true` y `venta_mayorista: true`.
3. Cada producto muestra `precio_mayorista` (COP por unidad), `cantidad_minima` y `condiciones_compra` tal como constan en `catalogo_mayorista.json`.

## Instalación en Windows (PowerShell)

1. Copiar **solo** `backend/hu17/` dentro del repositorio, **sin reemplazar** `backend/main.py` ni `backend/productos.json` de HU-06.
2. Abrir VS Code en la raíz del repositorio; abrir una terminal y entrar a la carpeta `backend`:

```powershell
cd backend
```

3. Crea un entorno virtual **dentro de `hu17`** para mantenerlo aislado de HU-06 y excluido mediante `hu17/.gitignore`:

```powershell
py -m venv hu17/.venv
.\hu17\.venv\Scripts\python.exe -m pip install -r hu17/requirements.txt pytest httpx
.\hu17\.venv\Scripts\python.exe -m uvicorn hu17.main:app --reload --port 8001
```

Si el entorno ya existe, omite el primer comando.

4. Visitar:
- Catálogo web: **http://127.0.0.1:8001/mayoristas**
- API: **http://127.0.0.1:8001/api/mayoristas/productos**
- Documentación Swagger: **http://127.0.0.1:8001/docs**

En este ejemplo HU-06 puede seguir ejecutándose en **8000** y HU-17 en **8001** sin conflictos.

## Ejecutar las pruebas

Desde la carpeta `backend`:

```powershell
.\hu17\.venv\Scripts\python.exe -m pytest hu17/tests/ -v
```

## Datos temporales

`catalogo_mayorista.json` incluye **cinco referencias ficticias para pruebas académicas**. Se muestran solo tres de ellas: hay una agotada y otra no habilitada para mayoristas. **Precios, cantidades mínimas y condiciones son ilustrativos**; deben ser validados con Laura antes de su publicación comercial.

No se implementó carrito, registro/login, pedido ni envío WhatsApp: pertenecen a otras historias de usuario o requieren definición de alcance.

## Integración con HU-06 y futura base de datos

HU-17 funciona por separado para que puedas realizar su Pull Request aunque HU-06 todavía no se haya fusionado con `develop`.

Cuando el equipo desee servir ambas funcionalidades con una sola aplicación, agregue en **`backend/main.py`** existente lo siguiente (solo después de acordarlo, **no está incluido en este PR**):

```python
from hu17.router import router as hu17_router
app.include_router(hu17_router)
```

El origen de datos está encapsulado en `hu17/repository.py`: sustituye `cargar_productos()` por una consulta a PostgreSQL cuando la BD esté preparada, manteniendo los mismos contratos de API.

## GitHub: rama y Pull Request

1. Confirmar cambios guardados (`git status`).
2. Cambiar a `develop` y actualizar `git pull --ff-only origin develop` (si tu `develop` local no existe, `git fetch origin` seguido de `git switch -c develop --track origin/develop`).
3. Crear la rama `git switch -c feature/hu-17-consultar-catalogo-mayorista`.
4. Copiar `backend/hu17/` dentro del repositorio. No sustituir los archivos de HU-06.
5. Ejecutar las pruebas y revisar `git status`.
6. Preparar solo HU-17: `git add backend/hu17/`.
7. Commit: `git commit -m "feat(hu-17): consultar catalogo mayorista"`.
8. Publicar: `git push -u origin feature/hu-17-consultar-catalogo-mayorista`.
9. Crear Pull Request **base: develop ← compare: feature/hu-17-consultar-catalogo-mayorista** y pedir revisión antes del merge.

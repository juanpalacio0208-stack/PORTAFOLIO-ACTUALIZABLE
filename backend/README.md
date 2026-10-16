# HU-06 — Consultar productos como administradora

Este módulo implementa la consulta de los productos registrados para **Importaciones Euroamericanas** en Python + FastAPI, usando `productos.json` como almacenamiento temporal. No necesita MySQL ni PostgreSQL. Es una **demostración local sin autenticación**: NO debe desplegarse públicamente hasta incorporar inicio de sesión y permisos administrativos.

## Cómo añadirlo en GitHub sin afectar el trabajo de otros

1. Verifica que estás en `feature/hu-06-consultar-productos-admin` con `git branch --show-current`.
2. Descomprime el ZIP y copia **solo la carpeta `backend/`** en la raíz de `PORTAFOLIO-ACTUALIZABLE/` (junto a `frontend/` si existe).
3. No borres `README.md` ni `.gitignore` que ya estén en la raíz del repositorio.
4. Si existe previamente `backend/`, consulta con el equipo antes de combinar archivos.

## Requisitos

- Windows 10/11 con Python 3.10 o posterior.
- Acceso a internet para la instalación inicial de librerías.

## Ejecutar en Visual Studio Code (PowerShell)

Abre una terminal en la raíz del repositorio y ejecuta **uno por uno**:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1
```

Abre:

- Interfaz de consulta: http://127.0.0.1:8000/admin/productos
- API (todos): http://127.0.0.1:8000/api/admin/productos
- API (producto 1): http://127.0.0.1:8000/api/admin/productos/1
- Documentación de la API: http://127.0.0.1:8000/docs

Para parar el servidor: `Ctrl+C`.

## Pruebas automáticas (opcional)

Desde `backend/`, en otra terminal:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest tests -q
```

## Casos de aceptación HU-06

- La administradora **puede consultar el listado** de productos registrados (disponibles y agotados).
- Puede conocer los **datos de cada producto** (ID, nombre, categoría, descripción, precio y disponibilidad).
- Las consultas reflejan **los valores actuales del archivo JSON**: se lee de nuevo en cada petición.
- Si no existe un producto consultado por ID devuelve HTTP 404.
- Si no hay productos, se presenta un mensaje informativo.

## Límites de esta entrega

- **No implementa login ni control de roles**. Las rutas `/admin` y `/api/admin` son accesibles mientras el servicio está iniciado. Úsalo solo en tu PC para desarrollo; no hagas el servidor público.
- Los productos son de ejemplo; no existe base de datos aún.
- No implementa crear, editar o eliminar productos: corresponden a otras historias de usuario.
- No sustituye ni necesita modificar el frontend React existente. La vista demo está servida por FastAPI.

## Migración futura a la base de datos

El método `cargar_productos()` de `main.py` concentra el acceso a datos. Después se sustituirá la lectura de `productos.json` por una consulta PostgreSQL/MySQL, manteniendo los endpoints (si los contratos siguen vigentes).

## Publicar esta HU en su rama

Desde la **raíz** de `PORTAFOLIO-ACTUALIZABLE`:

```powershell
git branch --show-current
git status
git add backend/
git status
git commit -m "feat(hu-06): consulta administrativa de productos con FastAPI"
git push -u origin feature/hu-06-consultar-productos-admin
```

No hagas merge a `main`. El PR debe ir a `develop` cuando tu equipo lo apruebe.


import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from hu12.security import obtener_usuario_autenticado

from .models import SolicitudCrear, SolicitudRespuesta
from .repository import obtener_producto

router = APIRouter(prefix="/api/solicitudes", tags=["HU-08 Solicitudes"])

ARCHIVO_SOLICITUDES = (
    Path(__file__).resolve().parent / "solicitudes.json"
)

_bloqueo = Lock()


@router.post("", response_model=SolicitudRespuesta, status_code=201)
def crear_solicitud(datos: SolicitudCrear, request: Request):
    producto = obtener_producto(datos.producto_id)

    solicitud = SolicitudRespuesta(
        id=str(uuid4()),
        producto_id=producto["id"],
        producto_nombre=producto["nombre"],
        estado="PENDIENTE_CONTACTO",
        fecha_creacion=datetime.now(timezone.utc),
    )

    # Al tener sesión, la solicitud pertenece a esa cuenta. Los anónimos
    # conservan el flujo existente, pero no aparecen en un historial privado.
    usuario_id = None
    if request.cookies.get("portafolio_sesion"):
        usuario_id = obtener_usuario_autenticado(request)["id"]

    with _bloqueo:
        try:
            if ARCHIVO_SOLICITUDES.exists():
                with ARCHIVO_SOLICITUDES.open(
                    "r", encoding="utf-8"
                ) as archivo:
                    solicitudes = json.load(archivo)
            else:
                solicitudes = []

            if not isinstance(solicitudes, list):
                raise ValueError("Formato de solicitudes inválido")

            registro = solicitud.model_dump(mode="json")
            if usuario_id is not None:
                registro["usuario_id"] = usuario_id
            solicitudes.append(registro)

            temporal = ARCHIVO_SOLICITUDES.with_suffix(".tmp")
            temporal.write_text(
                json.dumps(solicitudes, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            temporal.replace(ARCHIVO_SOLICITUDES)

        except (OSError, ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=500,
                detail="No fue posible guardar la solicitud.",
            ) from exc

    return solicitud

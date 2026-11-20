
import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from .models import SolicitudCrear, SolicitudRespuesta
from .repository import obtener_producto

router = APIRouter(prefix="/api/solicitudes", tags=["HU-08 Solicitudes"])

ARCHIVO_SOLICITUDES = (
    Path(__file__).resolve().parent / "solicitudes.json"
)

_bloqueo = Lock()


@router.post("", response_model=SolicitudRespuesta, status_code=201)
def crear_solicitud(datos: SolicitudCrear):
    producto = obtener_producto(datos.producto_id)

    solicitud = SolicitudRespuesta(
        id=str(uuid4()),
        producto_id=producto["id"],
        producto_nombre=producto["nombre"],
        estado="PENDIENTE_CONTACTO",
        fecha_creacion=datetime.now(timezone.utc),
    )

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

            solicitudes.append(
                solicitud.model_dump(mode="json")
            )

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

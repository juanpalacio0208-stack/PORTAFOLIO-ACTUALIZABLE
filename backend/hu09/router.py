
import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from hu08 import router as modulo_solicitudes
from .models import ContactoComprador

router = APIRouter(
    prefix="/api/solicitudes",
    tags=["HU-09 Contacto del comprador"],
)


@router.patch("/{solicitud_id}/contacto")
def guardar_contacto(
    solicitud_id: str,
    contacto: ContactoComprador,
):
    with modulo_solicitudes._bloqueo:
        archivo = modulo_solicitudes.ARCHIVO_SOLICITUDES

        try:
            if not archivo.exists():
                raise HTTPException(
                    status_code=404,
                    detail="La solicitud no existe.",
                )

            with archivo.open("r", encoding="utf-8") as f:
                solicitudes = json.load(f)

            if not isinstance(solicitudes, list):
                raise ValueError("Formato de solicitudes inválido")

            solicitud = next(
                (
                    item for item in solicitudes
                    if item.get("id") == solicitud_id
                ),
                None,
            )

            if solicitud is None:
                raise HTTPException(
                    status_code=404,
                    detail="La solicitud no existe.",
                )

            if solicitud.get("estado") not in (
                "PENDIENTE_CONTACTO",
                "CONTACTO_COMPLETADO",
            ):
                raise HTTPException(
                    status_code=409,
                    detail="La solicitud no permite modificar el contacto.",
                )

            solicitud["contacto"] = contacto.model_dump(
                mode="json"
            )
            solicitud["estado"] = "CONTACTO_COMPLETADO"
            solicitud["fecha_actualizacion"] = (
                datetime.now(timezone.utc).isoformat()
            )

            temporal = archivo.with_suffix(".tmp")
            temporal.write_text(
                json.dumps(
                    solicitudes,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            temporal.replace(archivo)

            return {
                "mensaje": "Datos de contacto guardados correctamente.",
                "solicitud_id": solicitud_id,
                "producto_id": solicitud["producto_id"],
                "estado": solicitud["estado"],
                "contacto": solicitud["contacto"],
            }

        except HTTPException:
            raise
        except (OSError, ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=500,
                detail="No fue posible guardar los datos de contacto.",
            ) from exc

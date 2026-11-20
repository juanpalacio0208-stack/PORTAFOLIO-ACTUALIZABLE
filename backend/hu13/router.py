from fastapi import APIRouter, Depends, HTTPException

from hu12.security import obtener_usuario_autenticado
from hu11 import repository
from .models import UsuarioAdministracion, UsuarioActualizacionAdmin
from .service import actualizar_usuario, listar_usuarios

router = APIRouter(prefix="/api/admin/usuarios", tags=["HU-13 Administrar usuarios"])


def requerir_administrador(usuario: dict = Depends(obtener_usuario_autenticado)):
    if usuario["rol"] != "administrador":
        raise HTTPException(status_code=403, detail="Se requiere rol de administrador.")
    return usuario


@router.get("", response_model=list[UsuarioAdministracion])
def consultar_usuarios(_: dict = Depends(requerir_administrador)):
    return listar_usuarios()


@router.patch("/{usuario_id}", response_model=UsuarioAdministracion)
def modificar_usuario(
    usuario_id: int,
    datos: UsuarioActualizacionAdmin,
    administrador: dict = Depends(requerir_administrador),
):
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if not cambios:
        raise HTTPException(status_code=422, detail="Indica el estado o el rol a actualizar.")
    if usuario_id == administrador["id"] and (
        cambios.get("activo") is False or cambios.get("rol") == "usuario"
    ):
        raise HTTPException(status_code=409, detail="No puedes desactivar ni cambiar tu propio rol.")
    actual = next((u for u in listar_usuarios() if u["id"] == usuario_id), None)
    if actual is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    degradando_admin = actual["rol"] == "administrador" and (
        cambios.get("activo") is False or cambios.get("rol") == "usuario"
    )
    if degradando_admin:
        otros_activos = [
            u for u in listar_usuarios()
            if u["id"] != usuario_id and u["activo"] and u["rol"] == "administrador"
        ]
        if not otros_activos:
            raise HTTPException(status_code=409, detail="Debe permanecer al menos un administrador activo.")
    usuario = actualizar_usuario(usuario_id, cambios)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if usuario_id == administrador["id"] and not usuario["activo"]:
        raise HTTPException(status_code=409, detail="No puedes desactivar tu propia cuenta.")
    return usuario

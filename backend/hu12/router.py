
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from hu11.repository import buscar_usuario_por_correo, password_hash
from hu11.repository import actualizar_perfil
from hu20.models import PerfilActualizacion
from .models import CredencialesLogin, RespuestaLogin, UsuarioAutenticado
from .security import (
    DURACION_SESION,
    NOMBRE_COOKIE,
    crear_sesion,
    eliminar_sesion,
    obtener_usuario_autenticado,
)

router = APIRouter(
    prefix="/api/auth",
    tags=["HU-12 Inicio de sesión"],
)


@router.post("/login", response_model=RespuestaLogin)
def iniciar_sesion(datos: CredencialesLogin, response: Response):
    usuario = buscar_usuario_por_correo(str(datos.correo))

    # Evita revelar si el correo está registrado.
    if usuario is None or not usuario["activo"]:
        raise HTTPException(
            status_code=401,
            detail="Correo electrónico o contraseña incorrectos.",
        )

    if not password_hash.verify(
        datos.contrasena,
        usuario["contrasena_hash"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Correo electrónico o contraseña incorrectos.",
        )

    try:
        token = crear_sesion(usuario["id"])
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail="No fue posible iniciar sesión.",
        ) from exc

    response.set_cookie(
        key=NOMBRE_COOKIE,
        value=token,
        max_age=int(DURACION_SESION.total_seconds()),
        httponly=True,
        secure=False,  # Solo desarrollo local HTTP
        samesite="lax",
        path="/",
    )

    return {
        "mensaje": "Inicio de sesión exitoso.",
        "usuario": {
            "id": usuario["id"],
            "nombre_completo": usuario["nombre_completo"],
            "correo": usuario["correo"],
            "activo": bool(usuario["activo"]),
            "rol": usuario["rol"],
        },
    }


@router.get("/me", response_model=UsuarioAutenticado)
def consultar_mi_cuenta(
    usuario: dict = Depends(obtener_usuario_autenticado),
):
    return usuario


@router.patch("/me", response_model=UsuarioAutenticado)
def actualizar_mi_perfil(
    datos: PerfilActualizacion,
    usuario: dict = Depends(obtener_usuario_autenticado),
):
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    try:
        actualizado = actualizar_perfil(int(usuario["id"]), cambios)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Este correo electrónico ya está registrado.") from exc
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="No fue posible actualizar el perfil.") from exc
    if actualizado is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {**actualizado, "activo": bool(actualizado["activo"])}


@router.post("/logout")
def cerrar_sesion(
    request: Request,
    response: Response,
):
    eliminar_sesion(request.cookies.get(NOMBRE_COOKIE))

    response.delete_cookie(
        key=NOMBRE_COOKIE,
        path="/",
        samesite="lax",
    )

    return {"mensaje": "Sesión cerrada correctamente."}

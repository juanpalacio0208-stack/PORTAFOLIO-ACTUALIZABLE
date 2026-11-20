import pytest
from fastapi.testclient import TestClient

from hu11 import repository
from main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(repository, "BASE_DATOS", tmp_path / "usuarios_test.db")
    with TestClient(app) as test_client:
        yield test_client


def registrar(client, correo):
    respuesta = client.post("/api/auth/registro", json={
        "nombre_completo": "Usuario Prueba", "correo": correo, "contrasena": "Prueba12345",
    })
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def autenticar(client, correo):
    respuesta = client.post("/api/auth/login", json={"correo": correo, "contrasena": "Prueba12345"})
    assert respuesta.status_code == 200


def hacer_admin(usuario_id):
    with repository.conectar() as conexion:
        conexion.execute("UPDATE usuarios SET rol = 'administrador' WHERE id = ?", (usuario_id,))


def test_listado_requiere_autenticacion_y_rol_admin(client):
    assert client.get("/api/admin/usuarios").status_code == 401
    registrar(client, "lector@example.com")
    autenticar(client, "lector@example.com")
    assert client.get("/api/admin/usuarios").status_code == 403


def test_admin_lista_cuentas_sin_datos_de_contrasena(client):
    admin_id = registrar(client, "admin@example.com")
    registrar(client, "persona@example.com")
    hacer_admin(admin_id)
    autenticar(client, "admin@example.com")
    respuesta = client.get("/api/admin/usuarios")
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 2
    assert all("contrasena" not in u and "contrasena_hash" not in u for u in respuesta.json())


def test_admin_cambia_rol_y_estado(client):
    admin_id = registrar(client, "admin@example.com")
    usuario_id = registrar(client, "persona@example.com")
    hacer_admin(admin_id)
    autenticar(client, "admin@example.com")
    cambio_rol = client.patch(f"/api/admin/usuarios/{usuario_id}", json={"rol": "administrador"})
    cambio_estado = client.patch(f"/api/admin/usuarios/{usuario_id}", json={"activo": False})
    assert cambio_rol.status_code == 200 and cambio_rol.json()["rol"] == "administrador"
    assert cambio_estado.status_code == 200 and cambio_estado.json()["activo"] is False


def test_admin_no_puede_quitarse_ni_eliminar_ultimo_admin(client):
    admin_id = registrar(client, "admin@example.com")
    hacer_admin(admin_id)
    autenticar(client, "admin@example.com")
    assert client.patch(f"/api/admin/usuarios/{admin_id}", json={"activo": False}).status_code == 409
    assert client.patch(f"/api/admin/usuarios/{admin_id}", json={"rol": "usuario"}).status_code == 409
    with repository.conectar() as conexion:
        assert conexion.execute("SELECT activo FROM usuarios WHERE id = ?", (admin_id,)).fetchone()[0] == 1


def test_usuario_no_encontrado_y_cambios_invalidos(client):
    admin_id = registrar(client, "admin@example.com")
    registrar(client, "regular@example.com")
    hacer_admin(admin_id)
    autenticar(client, "admin@example.com")
    assert client.patch("/api/admin/usuarios/999", json={"activo": False}).status_code == 404
    assert client.patch("/api/admin/usuarios/2", json={"rol": "superusuario"}).status_code == 422
    assert client.patch("/api/admin/usuarios/2", json={}).status_code == 422

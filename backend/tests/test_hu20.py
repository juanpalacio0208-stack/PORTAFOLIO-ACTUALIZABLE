import pytest
from fastapi.testclient import TestClient

from hu11 import repository
from main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(repository, "BASE_DATOS", tmp_path / "usuarios_test.db")
    with TestClient(app) as test_client:
        yield test_client


def crear_y_autenticar(client, correo="persona@example.com"):
    datos = {"nombre_completo": "Persona Prueba", "correo": correo, "contrasena": "Prueba12345"}
    assert client.post("/api/auth/registro", json=datos).status_code == 201
    assert client.post("/api/auth/login", json={"correo": correo, "contrasena": datos["contrasena"]}).status_code == 200


def test_actualizar_nombre_y_correo_propio(client):
    crear_y_autenticar(client)
    respuesta = client.patch("/api/auth/me", json={"nombre_completo": "Nombre Actualizado", "correo": "nuevo@example.com"})
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre_completo"] == "Nombre Actualizado"
    assert respuesta.json()["correo"] == "nuevo@example.com"
    assert "contrasena_hash" not in respuesta.json()
    assert client.get("/api/auth/me").json()["correo"] == "nuevo@example.com"


def test_actualizar_contrasena_almacena_hash_y_nueva_clave_permite_login(client):
    crear_y_autenticar(client)
    respuesta = client.patch("/api/auth/me", json={"contrasena": "NuevaClave123"})
    assert respuesta.status_code == 200
    with repository.conectar() as conexion:
        hash_guardado = conexion.execute("SELECT contrasena_hash FROM usuarios").fetchone()[0]
    assert hash_guardado != "NuevaClave123"
    assert repository.password_hash.verify("NuevaClave123", hash_guardado)
    client.post("/api/auth/logout")
    assert client.post("/api/auth/login", json={"correo": "persona@example.com", "contrasena": "NuevaClave123"}).status_code == 200


def test_actualizar_perfil_requiere_sesion_y_rechaza_correo_duplicado(client):
    client.post("/api/auth/registro", json={"nombre_completo": "Una Persona", "correo": "una@example.com", "contrasena": "Prueba12345"})
    assert client.patch("/api/auth/me", json={"nombre_completo": "Otro Nombre"}).status_code == 401
    crear_y_autenticar(client, "dos@example.com")
    respuesta = client.patch("/api/auth/me", json={"correo": "una@example.com"})
    assert respuesta.status_code == 409


@pytest.mark.parametrize("cambios", [{}, {"nombre_completo": "  "}, {"correo": "correo-invalido"}, {"contrasena": "sololetras"}])
def test_rechaza_cambios_invalidos(client, cambios):
    crear_y_autenticar(client)
    assert client.patch("/api/auth/me", json=cambios).status_code == 422

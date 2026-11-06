
import pytest
from fastapi.testclient import TestClient

from main import app
from hu11 import repository

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(
        repository,
        "BASE_DATOS",
        tmp_path / "usuarios_test.db",
    )

    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture
def comprador_registrado(client):
    datos = {
        "nombre_completo": "Comprador Prueba",
        "correo": "comprador@example.com",
        "contrasena": "Prueba12345",
    }

    respuesta = client.post("/api/auth/registro", json=datos)
    assert respuesta.status_code == 201

    return datos


def test_login_correcto(client, comprador_registrado):
    respuesta = client.post(
        "/api/auth/login",
        json={
            "correo": comprador_registrado["correo"],
            "contrasena": comprador_registrado["contrasena"],
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["mensaje"] == "Inicio de sesión exitoso."
    assert respuesta.json()["usuario"]["correo"] == comprador_registrado["correo"]


def test_login_contrasena_incorrecta(client, comprador_registrado):
    respuesta = client.post(
        "/api/auth/login",
        json={
            "correo": comprador_registrado["correo"],
            "contrasena": "Incorrecta123",
        },
    )

    assert respuesta.status_code == 401


def test_login_correo_inexistente(client):
    respuesta = client.post(
        "/api/auth/login",
        json={
            "correo": "inexistente@example.com",
            "contrasena": "Prueba12345",
        },
    )

    assert respuesta.status_code == 401


def test_login_campos_obligatorios(client):
    respuesta = client.post(
        "/api/auth/login",
        json={
            "correo": "",
            "contrasena": "",
        },
    )

    assert respuesta.status_code == 422


def test_consultar_cuenta_autenticada(client, comprador_registrado):
    client.post(
        "/api/auth/login",
        json={
            "correo": comprador_registrado["correo"],
            "contrasena": comprador_registrado["contrasena"],
        },
    )

    respuesta = client.get("/api/auth/me")

    assert respuesta.status_code == 200
    assert respuesta.json()["correo"] == comprador_registrado["correo"]


def test_cuenta_sin_autenticacion(client):
    respuesta = client.get("/api/auth/me")
    assert respuesta.status_code == 401


def test_cerrar_sesion(client, comprador_registrado):
    client.post(
        "/api/auth/login",
        json={
            "correo": comprador_registrado["correo"],
            "contrasena": comprador_registrado["contrasena"],
        },
    )

    respuesta = client.post("/api/auth/logout")
    assert respuesta.status_code == 200

    respuesta_cuenta = client.get("/api/auth/me")
    assert respuesta_cuenta.status_code == 401

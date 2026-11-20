
import sqlite3

import pytest
from fastapi.testclient import TestClient

from main import app
from hu11 import repository

client = TestClient(app)


@pytest.fixture(autouse=True)
def base_datos_temporal(tmp_path, monkeypatch):
    monkeypatch.setattr(
        repository,
        "BASE_DATOS",
        tmp_path / "usuarios_test.db",
    )


def test_registrar_usuario_correctamente():
    respuesta = client.post(
        "/api/auth/registro",
        json={
            "nombre_completo": "Comprador Prueba",
            "correo": "comprador@example.com",
            "contrasena": "Prueba12345",
        },
    )

    assert respuesta.status_code == 201

    usuario = respuesta.json()
    assert usuario["nombre_completo"] == "Comprador Prueba"
    assert usuario["correo"] == "comprador@example.com"
    assert usuario["activo"] is True
    assert "contrasena" not in usuario
    assert "contrasena_hash" not in usuario


def test_rechazar_correo_duplicado():
    datos = {
        "nombre_completo": "Comprador Prueba",
        "correo": "duplicado@example.com",
        "contrasena": "Prueba12345",
    }

    primera = client.post("/api/auth/registro", json=datos)
    segunda = client.post("/api/auth/registro", json=datos)

    assert primera.status_code == 201
    assert segunda.status_code == 409


def test_rechazar_nombre_vacio():
    respuesta = client.post(
        "/api/auth/registro",
        json={
            "nombre_completo": "",
            "correo": "nombre@example.com",
            "contrasena": "Prueba12345",
        },
    )

    assert respuesta.status_code == 422


def test_rechazar_correo_invalido():
    respuesta = client.post(
        "/api/auth/registro",
        json={
            "nombre_completo": "Comprador Prueba",
            "correo": "correo-invalido",
            "contrasena": "Prueba12345",
        },
    )

    assert respuesta.status_code == 422


def test_rechazar_contrasena_debil():
    respuesta = client.post(
        "/api/auth/registro",
        json={
            "nombre_completo": "Comprador Prueba",
            "correo": "debil@example.com",
            "contrasena": "12345678",
        },
    )

    assert respuesta.status_code == 422


def test_contrasena_guardada_como_hash():
    respuesta = client.post(
        "/api/auth/registro",
        json={
            "nombre_completo": "Comprador Prueba",
            "correo": "seguro@example.com",
            "contrasena": "Prueba12345",
        },
    )

    assert respuesta.status_code == 201

    with sqlite3.connect(repository.BASE_DATOS) as conexion:
        fila = conexion.execute(
            "SELECT contrasena_hash FROM usuarios WHERE correo = ?",
            ("seguro@example.com",),
        ).fetchone()

    assert fila is not None
    assert fila[0] != "Prueba12345"
    assert fila[0].startswith("$argon2")
    assert repository.password_hash.verify("Prueba12345", fila[0])

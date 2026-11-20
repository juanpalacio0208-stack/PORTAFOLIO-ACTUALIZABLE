
from fastapi.testclient import TestClient

from main import app
from hu08 import router as modulo_solicitudes

client = TestClient(app)


def test_crear_solicitud_producto_disponible(tmp_path, monkeypatch):
    archivo = tmp_path / "solicitudes.json"
    monkeypatch.setattr(
        modulo_solicitudes, "ARCHIVO_SOLICITUDES", archivo
    )

    respuesta = client.post(
        "/api/solicitudes",
        json={"producto_id": 1},
    )

    assert respuesta.status_code == 201

    datos = respuesta.json()
    assert datos["producto_id"] == 1
    assert datos["producto_nombre"] == "Body Wash EOS Vanilla Cashmere"
    assert datos["estado"] == "PENDIENTE_CONTACTO"
    assert datos["id"]
    assert archivo.exists()


def test_rechazar_producto_agotado():
    respuesta = client.post(
        "/api/solicitudes",
        json={"producto_id": 3},
    )

    assert respuesta.status_code == 409


def test_rechazar_producto_inexistente():
    respuesta = client.post(
        "/api/solicitudes",
        json={"producto_id": 999},
    )

    assert respuesta.status_code == 404


def test_rechazar_identificador_invalido():
    respuesta = client.post(
        "/api/solicitudes",
        json={"producto_id": -1},
    )

    assert respuesta.status_code == 422

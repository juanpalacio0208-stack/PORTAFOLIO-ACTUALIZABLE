
import json

import pytest
from fastapi.testclient import TestClient

from main import app
from hu08 import router as modulo_solicitudes

client = TestClient(app)


@pytest.fixture
def solicitud_prueba(tmp_path, monkeypatch):
    archivo = tmp_path / "solicitudes.json"

    monkeypatch.setattr(
        modulo_solicitudes,
        "ARCHIVO_SOLICITUDES",
        archivo,
    )

    respuesta = client.post(
        "/api/solicitudes",
        json={"producto_id": 1},
    )

    assert respuesta.status_code == 201

    return respuesta.json()["id"], archivo


def test_guardar_contacto_valido(solicitud_prueba):
    solicitud_id, archivo = solicitud_prueba

    respuesta = client.patch(
        f"/api/solicitudes/{solicitud_id}/contacto",
        json={
            "nombre_completo": "Comprador de Prueba",
            "telefono": "3001234567",
            "correo": "comprador@example.com",
        },
    )

    assert respuesta.status_code == 200

    datos = respuesta.json()
    assert datos["estado"] == "CONTACTO_COMPLETADO"
    assert datos["contacto"]["nombre_completo"] == "Comprador de Prueba"

    solicitudes = json.loads(archivo.read_text(encoding="utf-8"))
    assert solicitudes[0]["contacto"]["telefono"] == "3001234567"


def test_rechazar_nombre_vacio(solicitud_prueba):
    solicitud_id, _ = solicitud_prueba

    respuesta = client.patch(
        f"/api/solicitudes/{solicitud_id}/contacto",
        json={
            "nombre_completo": "",
            "telefono": "3001234567",
        },
    )

    assert respuesta.status_code == 422


def test_rechazar_telefono_vacio(solicitud_prueba):
    solicitud_id, _ = solicitud_prueba

    respuesta = client.patch(
        f"/api/solicitudes/{solicitud_id}/contacto",
        json={
            "nombre_completo": "Comprador de Prueba",
            "telefono": "",
        },
    )

    assert respuesta.status_code == 422


def test_rechazar_correo_invalido(solicitud_prueba):
    solicitud_id, _ = solicitud_prueba

    respuesta = client.patch(
        f"/api/solicitudes/{solicitud_id}/contacto",
        json={
            "nombre_completo": "Comprador de Prueba",
            "telefono": "3001234567",
            "correo": "correo-invalido",
        },
    )

    assert respuesta.status_code == 422


def test_solicitud_inexistente():
    respuesta = client.patch(
        "/api/solicitudes/identificador-inexistente/contacto",
        json={
            "nombre_completo": "Comprador de Prueba",
            "telefono": "3001234567",
        },
    )

    assert respuesta.status_code == 404


def test_datos_invalidos_no_modifican_solicitud(solicitud_prueba):
    solicitud_id, archivo = solicitud_prueba

    respuesta = client.patch(
        f"/api/solicitudes/{solicitud_id}/contacto",
        json={
            "nombre_completo": "",
            "telefono": "",
        },
    )

    assert respuesta.status_code == 422

    solicitudes = json.loads(archivo.read_text(encoding="utf-8"))
    assert solicitudes[0]["estado"] == "PENDIENTE_CONTACTO"
    assert "contacto" not in solicitudes[0]

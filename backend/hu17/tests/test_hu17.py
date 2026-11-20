"""Pruebas de los tres criterios de aceptación HU-17 y manejo de errores."""

import json

import pytest
from fastapi.testclient import TestClient

from hu17 import repository
from hu17.main import app

client = TestClient(app)


def test_el_cliente_accede_al_catalogo_mayorista():
    respuesta = client.get("/mayoristas")
    assert respuesta.status_code == 200
    assert "Catálogo" in respuesta.text
    assert "mayorista" in respuesta.text


def test_lista_solo_productos_disponibles_para_mayoristas():
    respuesta = client.get("/api/mayoristas/productos")
    assert respuesta.status_code == 200
    ids = {p["id"] for p in respuesta.json()}
    assert ids == {1, 2, 4}
    assert all(p["disponible"] and p["venta_mayorista"] for p in respuesta.json())


def test_precios_y_condiciones_coinciden_con_los_datos_registrados():
    with repository.ARCHIVO_PRODUCTOS.open(encoding="utf-8") as f:
        originales = {p["id"]: p for p in json.load(f)}
    respuesta = client.get("/api/mayoristas/productos")
    for producto in respuesta.json():
        original = originales[producto["id"]]
        assert producto["precio_mayorista"] == original["precio_mayorista"]
        assert producto["cantidad_minima"] == original["cantidad_minima"]
        assert producto["condiciones_compra"] == original["condiciones_compra"]
        assert original["condiciones_compra"] in client.get("/mayoristas").text


def test_consulta_individual():
    respuesta = client.get("/api/mayoristas/productos/1")
    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == 1


@pytest.mark.parametrize("id_no_disponible", [3, 5, 999])
def test_individual_no_exponer_agotados_ni_no_mayoristas(id_no_disponible):
    respuesta = client.get(f"/api/mayoristas/productos/{id_no_disponible}")
    assert respuesta.status_code == 404


def test_lee_cambios_del_json_sin_reiniciar(monkeypatch, tmp_path):
    archivo = tmp_path / "mayoristas.json"
    with repository.ARCHIVO_PRODUCTOS.open(encoding="utf-8") as fuente:
        productos = json.load(fuente)
    archivo.write_text(json.dumps(productos, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(repository, "ARCHIVO_PRODUCTOS", archivo)
    productos[0]["precio_mayorista"] = 12345
    archivo.write_text(json.dumps(productos, ensure_ascii=False), encoding="utf-8")
    respuesta = client.get("/api/mayoristas/productos/1")
    assert respuesta.json()["precio_mayorista"] == 12345


def test_json_corrupto_responde_error_controlado(monkeypatch, tmp_path):
    archivo = tmp_path / "roto.json"
    archivo.write_text("{esto no es JSON}", encoding="utf-8")
    monkeypatch.setattr(repository, "ARCHIVO_PRODUCTOS", archivo)
    respuesta = client.get("/api/mayoristas/productos")
    assert respuesta.status_code == 500
    assert respuesta.json()["detail"] == "No se pudo consultar el catálogo mayorista."


def test_html_escapa_datos_no_confiables(monkeypatch, tmp_path):
    archivo = tmp_path / "html.json"
    producto = {
        "id": 7,
        "nombre": '<script>alert("x")</script>',
        "descripcion": "Descripción",
        "categoria": "Otro",
        "precio_mayorista": 1000,
        "cantidad_minima": 2,
        "condiciones_compra": '<img src=x onerror=alert(1)>',
        "disponible": True,
        "venta_mayorista": True,
    }
    archivo.write_text(json.dumps([producto]), encoding="utf-8")
    monkeypatch.setattr(repository, "ARCHIVO_PRODUCTOS", archivo)
    respuesta = client.get("/mayoristas")
    assert respuesta.status_code == 200
    assert "<script>" not in respuesta.text
    assert "<img src=x" not in respuesta.text
    assert "&lt;script&gt;" in respuesta.text


def test_vista_sin_productos(monkeypatch, tmp_path):
    archivo = tmp_path / "vacio.json"
    archivo.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(repository, "ARCHIVO_PRODUCTOS", archivo)
    respuesta = client.get("/mayoristas")
    assert "No hay productos mayoristas disponibles" in respuesta.text


def test_recursos_estaticos():
    assert client.get("/mayoristas/estilos.css").status_code == 200
    assert client.get("/mayoristas/logo.png").status_code == 200

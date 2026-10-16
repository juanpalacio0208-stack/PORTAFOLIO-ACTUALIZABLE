import json

import pytest
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def test_consultar_todos_los_productos():
    response = client.get('/api/admin/productos')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    assert any(p['disponible'] is False for p in data)


def test_consultar_producto_por_id():
    response = client.get('/api/admin/productos/1')
    assert response.status_code == 200
    assert response.json()['nombre'] == 'Body Wash EOS Vanilla Cashmere'


def test_producto_inexistente_devuelve_404():
    response = client.get('/api/admin/productos/999')
    assert response.status_code == 404


def test_panel_presenta_productos():
    response = client.get('/admin/productos')
    assert response.status_code == 200
    assert 'Body Wash EOS Vanilla Cashmere' in response.text
    assert 'Agotado' in response.text


def test_lectura_refleja_modificaciones_del_json(tmp_path, monkeypatch):
    archivo = tmp_path / 'productos.json'
    archivo.write_text(json.dumps([{'id': 20, 'nombre': 'Nuevo', 'descripcion': 'Demo', 'categoria': 'Otros', 'precio': 12345, 'disponible': True}]), encoding='utf-8')
    monkeypatch.setattr(main, 'ARCHIVO_PRODUCTOS', archivo)
    response = client.get('/api/admin/productos')
    assert response.status_code == 200
    assert response.json()[0]['nombre'] == 'Nuevo'
    assert len(response.json()) == 1


def test_json_corrupto_devuelve_error_controlado(tmp_path, monkeypatch):
    archivo = tmp_path / 'productos.json'
    archivo.write_text('{mal-json', encoding='utf-8')
    monkeypatch.setattr(main, 'ARCHIVO_PRODUCTOS', archivo)
    response = client.get('/api/admin/productos')
    assert response.status_code == 500
    assert response.json()['detail'] == 'No fue posible leer los productos almacenados.'


def test_escape_html_de_producto(tmp_path, monkeypatch):
    archivo = tmp_path / 'productos.json'
    archivo.write_text(json.dumps([{'id': 3, 'nombre': '<script>alert(1)</script>', 'descripcion': '<b>demo</b>', 'categoria': 'Demo', 'precio': 1, 'disponible': True}]), encoding='utf-8')
    monkeypatch.setattr(main, 'ARCHIVO_PRODUCTOS', archivo)
    response = client.get('/admin/productos')
    assert response.status_code == 200
    assert '<script>' not in response.text
    assert '&lt;script&gt;' in response.text

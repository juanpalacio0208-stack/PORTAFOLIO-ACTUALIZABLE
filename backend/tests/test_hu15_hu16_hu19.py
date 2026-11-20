"""Pruebas de las nuevas HU con almacenamiento temporal, sin servicios externos."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app
from hu11 import repository
from hu08 import router as hu08
from hu15_16_19 import router as nuevas


def test_consentimiento_filtro_envio_historial(tmp_path, monkeypatch):
    monkeypatch.setattr(repository, 'BASE_DATOS', tmp_path / 'usuarios.db')
    monkeypatch.setattr(hu08, 'ARCHIVO_SOLICITUDES', tmp_path / 'solicitudes.json')
    monkeypatch.setenv('PORTAFOLIO_ADMIN_EMAILS', 'admin@example.com')
    cliente_admin = TestClient(app)
    cliente_comprador = TestClient(app)
    cliente_sin_permiso = TestClient(app)

    for cliente, correo in ((cliente_admin, 'admin@example.com'), (cliente_comprador, 'comprador@example.com'), (cliente_sin_permiso, 'sinpermiso@example.com')):
        r = cliente.post('/api/auth/registro', json={'nombre_completo':'Usuario Ejemplo', 'correo':correo, 'contrasena':'Clave12345'})
        assert r.status_code == 201, r.text
        assert cliente.post('/api/auth/login', json={'correo':correo, 'contrasena':'Clave12345'}).status_code == 200

    assert cliente_comprador.get('/api/notificaciones/consentimiento').json() == {'autorizado': False}
    assert cliente_comprador.put('/api/notificaciones/consentimiento', json={'autorizado': True}).status_code == 200
    assert cliente_sin_permiso.post('/api/admin/notificaciones', json={'tipo':'descuento','titulo':'Prueba','mensaje':'Mensaje prueba'}).status_code == 403

    envio = cliente_admin.post('/api/admin/notificaciones', json={'tipo':'descuento','titulo':'Oferta especial','mensaje':'Nueva promoción'})
    assert envio.status_code == 201
    assert envio.json()['destinatarios'] == 1
    recibidas = cliente_comprador.get('/api/notificaciones/mias').json()
    assert len(recibidas) == 1
    assert cliente_sin_permiso.get('/api/notificaciones/mias').json() == []
    assert cliente_admin.patch(f"/api/notificaciones/{recibidas[0]['id']}/leida").status_code == 404
    assert cliente_comprador.patch(f"/api/notificaciones/{recibidas[0]['id']}/leida").status_code == 200

    # Simular solicitud asociada explícitamente a una cuenta (evita inferir titularidad por correo).
    usuario_comprador = repository.buscar_usuario_por_correo('comprador@example.com')
    hu08.ARCHIVO_SOLICITUDES.write_text(json.dumps([
        {'id':'solicitada', 'usuario_id':usuario_comprador['id'], 'producto_id':1, 'producto_nombre':'Producto A', 'estado':'CONTACTO_COMPLETADO', 'fecha_creacion':'2026-11-19T12:00:00+00:00'},
        {'id':'anonima', 'producto_id':1, 'producto_nombre':'Producto B', 'estado':'PENDIENTE_CONTACTO', 'fecha_creacion':'2026-11-19T12:01:00+00:00'},
    ]), encoding='utf-8')
    assert [s['id'] for s in cliente_comprador.get('/api/solicitudes/mias').json()] == ['solicitada']
    assert cliente_sin_permiso.get('/api/solicitudes/mias').json() == []

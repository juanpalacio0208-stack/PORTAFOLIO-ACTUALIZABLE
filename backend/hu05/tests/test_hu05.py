import json
import pytest
from fastapi.testclient import TestClient
from hu05 import repository as repo
from hu05.main import app

@pytest.fixture
def client(tmp_path,monkeypatch):
    p=tmp_path/'productos.json'
    p.write_text(json.dumps([{'id':1,'nombre':'Original','descripcion':'Antes','categoria':'Belleza','precio':5000,'disponible':False}],ensure_ascii=False),encoding='utf-8')
    monkeypatch.setattr(repo,'DATA_PATH',p)
    return TestClient(app),p

body={'nombre':'Actualizado','descripcion':'Después','categoria':'Cuidado personal','precio':23000}

def test_editar_y_guardar(client):
    c,p=client
    r=c.put('/api/hu05/productos/1',json=body)
    assert r.status_code==200 and r.json()['nombre']=='Actualizado'
    assert json.loads(p.read_text(encoding='utf-8'))[0]['precio']==23000

def test_mantiene_disponibilidad(client):
    c,p=client
    c.put('/api/hu05/productos/1',json=body)
    assert json.loads(p.read_text(encoding='utf-8'))[0]['disponible'] is False

def test_valida_requeridos(client):
    c,_=client
    assert c.put('/api/hu05/productos/1',json={**body,'nombre':'  '}).status_code==422
    assert c.put('/api/hu05/productos/1',json={**body,'precio':0}).status_code==422

def test_producto_inexistente(client):
    c,_=client
    assert c.put('/api/hu05/productos/777',json=body).status_code==404

def test_panel_y_listado(client):
    c,_=client
    assert c.get('/admin/editar-producto').status_code==200
    assert c.get('/api/hu05/productos').json()[0]['nombre']=='Original'

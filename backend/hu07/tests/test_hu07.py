import json
import pytest
from fastapi.testclient import TestClient
from hu07 import repository as repo
from hu07.main import app

@pytest.fixture
def client(tmp_path,monkeypatch):
    archivo=tmp_path/'productos.json'
    archivo.write_text(json.dumps([{'id':1,'nombre':'Crema','descripcion':'Corporal','categoria':'Belleza','precio':5000,'disponible':True}],ensure_ascii=False),encoding='utf-8')
    monkeypatch.setattr(repo,'DATA_PATH',archivo)
    return TestClient(app),archivo

def test_guarda_agotado(client):
    c,p=client
    r=c.patch('/api/hu07/productos/1/disponibilidad',json={'disponible':False})
    assert r.status_code==200 and r.json()['disponible'] is False
    assert json.loads(p.read_text(encoding='utf-8'))[0]['disponible'] is False

def test_refleja_catalogo(client):
    c,_=client
    assert len(c.get('/api/hu07/catalogo').json())==1
    c.patch('/api/hu07/productos/1/disponibilidad',json={'disponible':False})
    assert c.get('/api/hu07/catalogo').json()==[]
    c.patch('/api/hu07/productos/1/disponibilidad',json={'disponible':True})
    assert len(c.get('/api/hu07/catalogo').json())==1

def test_id_inexistente(client):
    c,_=client
    assert c.patch('/api/hu07/productos/9/disponibilidad',json={'disponible':False}).status_code==404

def test_valida_booleano(client):
    c,_=client
    assert c.patch('/api/hu07/productos/1/disponibilidad',json={'disponible':'cualquiera'}).status_code==422

def test_paginas(client):
    c,_=client
    assert c.get('/admin/disponibilidad').status_code==200
    assert c.get('/catalogo').status_code==200

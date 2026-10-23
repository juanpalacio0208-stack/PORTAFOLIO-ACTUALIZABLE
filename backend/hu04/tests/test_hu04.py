import json
import pytest
from fastapi.testclient import TestClient
from hu04 import repository as repo
from hu04.main import app

@pytest.fixture
def client(tmp_path,monkeypatch):
    archivo=tmp_path/'productos.json'
    archivo.write_text('[{"id":1,"nombre":"Original","descripcion":"Descripción","categoria":"Belleza","precio":1000,"disponible":true}]',encoding='utf-8')
    monkeypatch.setattr(repo,'DATA_PATH',archivo)
    return TestClient(app),archivo

def test_registrar_se_guarda(client):
    c,f=client
    r=c.post('/api/hu04/productos',json={'nombre':'Jabón','descripcion':'Corporal','categoria':'Cuidado','precio':35000,'disponible':True})
    assert r.status_code==201 and r.json()['id']==2
    assert len(json.loads(f.read_text(encoding='utf-8')))==2

def test_obligatorios_y_precio(client):
    c,_=client
    base={'nombre':'Jabón','descripcion':'Corporal','categoria':'Cuidado','precio':35000,'disponible':True}
    assert c.post('/api/hu04/productos',json={**base,'nombre':'  '}).status_code==422
    assert c.post('/api/hu04/productos',json={**base,'precio':-1}).status_code==422
    assert c.post('/api/hu04/productos',json={k:v for k,v in base.items() if k!='categoria'}).status_code==422

def test_disponibilidad_se_registra(client):
    c,f=client
    r=c.post('/api/hu04/productos',json={'nombre':'Jabón','descripcion':'Corporal','categoria':'Cuidado','precio':35000,'disponible':False})
    assert r.status_code==201 and r.json()['disponible'] is False
    assert json.loads(f.read_text(encoding='utf-8'))[-1]['disponible'] is False

def test_pagina_y_listado(client):
    c,_=client
    assert c.get('/admin/agregar-producto').status_code==200
    assert len(c.get('/api/hu04/productos').json())==1

def test_no_crear_archivo_si_falta(client):
    c,f=client
    f.unlink()
    r=c.post('/api/hu04/productos',json={'nombre':'Jabón','descripcion':'Corporal','categoria':'Cuidado','precio':35000,'disponible':True})
    assert r.status_code==503 and not f.exists()


def test_cambiar_disponibilidad_al_registrar_refleja_catalogo(client):
    c,_=client
    nuevo={'nombre':'Jabón','descripcion':'Corporal','categoria':'Cuidado','precio':35000,'disponible':False}
    assert c.post('/api/hu04/productos',json=nuevo).status_code==201
    assert len(c.get('/api/hu04/catalogo').json())==1
    nuevo['disponible']=True
    assert c.post('/api/hu04/productos',json=nuevo).status_code==201
    assert len(c.get('/api/hu04/catalogo').json())==2
    assert c.get('/catalogo').status_code==200

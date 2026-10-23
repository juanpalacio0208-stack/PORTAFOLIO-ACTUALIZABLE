"""Persistencia local para prototipo académico. Acceso admin no autenticado: sólo localhost."""
import json
import os
import threading
from pathlib import Path
from fastapi import HTTPException

DATA_PATH = Path(__file__).resolve().parent.parent / "productos.json"
_MUTEX = threading.RLock()


def leer():
    try:
        with DATA_PATH.open(encoding="utf-8") as f:
            datos=json.load(f)
        if not isinstance(datos,list) or any(not isinstance(x,dict) for x in datos):
            raise ValueError("Datos no son lista de objetos")
        return datos
    except FileNotFoundError as e:
        raise HTTPException(503,"No se encontró backend/productos.json (archivo de HU-06). No se ha modificado ningún archivo.") from e
    except (OSError, ValueError) as e:
        raise HTTPException(500,"No se puede leer backend/productos.json") from e


def guardar(productos):
    tmp=DATA_PATH.with_name(DATA_PATH.name+'.tmp')
    try:
        with tmp.open('w',encoding='utf-8') as f:
            json.dump(productos,f,ensure_ascii=False,indent=2)
            f.write('\n')
        os.replace(tmp,DATA_PATH)
    except OSError as e:
        raise HTTPException(500,'No fue posible guardar los productos') from e


def buscar(productos,identificador):
    return next((p for p in productos if p.get('id')==identificador),None)


def bloqueo():
    return _MUTEX


from datetime import datetime
from pydantic import BaseModel, Field


class SolicitudCrear(BaseModel):
    producto_id: int = Field(gt=0)


class SolicitudRespuesta(BaseModel):
    id: str
    producto_id: int
    producto_nombre: str
    estado: str
    fecha_creacion: datetime

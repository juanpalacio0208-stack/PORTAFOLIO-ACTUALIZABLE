"""Pruebas HU-18 con unittest (sin dependencias nuevas para pruebas)."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from fastapi import HTTPException

from hu11 import repository
from hu12.security import crear_sesion
from hu18 import service


class PruebasHU18(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.base = Path(self.temporal.name) / "usuarios.db"
        self.buzon = Path(self.temporal.name) / "buzon.txt"
        self.patch_bd = patch.object(repository, "BASE_DATOS", self.base)
        self.patch_buzon = patch.object(service, "RUTA_BUZON_DEMO", self.buzon)
        self.patch_entorno = patch.dict(os.environ, {
            "HU18_MODO_DEMO": "1",
            "HU18_FRONTEND_URL": "http://localhost:5173",
        })
        self.patch_bd.start()
        self.patch_buzon.start()
        self.patch_entorno.start()
        self.addCleanup(self.patch_bd.stop)
        self.addCleanup(self.patch_buzon.stop)
        self.addCleanup(self.patch_entorno.stop)

        # sqlite3.Connection no se cierra automaticamente con "with".
        # En Windows debemos cerrar las conexiones antes de borrar la BD temporal.
        conexiones_temporales = []
        conectar_original = repository.conectar

        def conectar_prueba():
            conexion = conectar_original()
            conexiones_temporales.append(conexion)
            return conexion

        self.patch_conectar = patch.object(repository, "conectar", conectar_prueba)
        self.patch_conectar.start()
        self.addCleanup(self.patch_conectar.stop)
        self.addCleanup(lambda: [conexion.close() for conexion in conexiones_temporales])

        repository.inicializar_base_datos()
        with repository.conectar() as conn:
            conn.execute(
                "INSERT INTO usuarios (nombre_completo, correo, contrasena_hash) "
                "VALUES (?, ?, ?)",
                ("Cliente Prueba", "cliente@example.com",
                 repository.password_hash.hash("ContrasenaOriginal123")),
            )

    def _token_generado(self):
        contenido = self.buzon.read_text(encoding="utf-8")
        url = contenido.split("Enlace: ")[-1].splitlines()[0]
        return parse_qs(urlsplit(url).fragment)["recuperar_token"][0]

    def test_correo_desconocido_respuesta_generica(self):
        respuesta = service.solicitar_recuperacion("desconocido@example.com")
        self.assertEqual(respuesta, service.MENSAJE_GENERICO)
        self.assertFalse(self.buzon.exists())

    def test_restaurar_clave_e_invalidar_sesion_y_token(self):
        usuario = repository.buscar_usuario_por_correo("cliente@example.com")
        crear_sesion(usuario["id"])
        respuesta = service.solicitar_recuperacion("cliente@example.com")
        self.assertEqual(respuesta, service.MENSAJE_GENERICO)
        token = self._token_generado()
        service.restablecer_contrasena(token, "NuevaContrasena123")
        actualizado = repository.buscar_usuario_por_correo("cliente@example.com")
        self.assertTrue(repository.password_hash.verify(
            "NuevaContrasena123", actualizado["contrasena_hash"]
        ))
        with repository.conectar() as conn:
            cantidad = conn.execute("SELECT COUNT(*) FROM sesiones").fetchone()[0]
        self.assertEqual(cantidad, 0)
        with self.assertRaises(HTTPException) as error:
            service.restablecer_contrasena(token, "SegundaClave123")
        self.assertEqual(error.exception.status_code, 400)

    def test_token_vencido_no_se_acepta(self):
        service.solicitar_recuperacion("cliente@example.com")
        token = self._token_generado()
        with repository.conectar() as conn:
            conn.execute("UPDATE recuperaciones_contrasena SET vence_en = 1")
        with self.assertRaises(HTTPException) as error:
            service.restablecer_contrasena(token, "NuevaContrasena123")
        self.assertEqual(error.exception.status_code, 400)

    def test_limite_una_solicitud_por_minuto(self):
        service.solicitar_recuperacion("cliente@example.com")
        primer_buzon = self.buzon.read_text(encoding="utf-8")
        service.solicitar_recuperacion("cliente@example.com")
        self.assertEqual(self.buzon.read_text(encoding="utf-8"), primer_buzon)


if __name__ == "__main__":
    unittest.main()

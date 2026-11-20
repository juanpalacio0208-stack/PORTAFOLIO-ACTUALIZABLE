"""Pruebas funcionales HU-14 sin modificar la base de datos real."""

import gc
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hu11 import repository
from hu14 import service


class TestHU14(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.limpiar_temporal)
        self.basedatos = Path(self.temporal.name) / "usuarios.db"
        self.parche = patch.object(repository, "BASE_DATOS", self.basedatos)
        self.parche.start()
        self.addCleanup(self.parche.stop)
        repository.inicializar_base_datos()
        with repository.conectar() as conexion:
            conexion.execute(
                "INSERT INTO usuarios (id, nombre_completo, correo, contrasena_hash) VALUES (?, ?, ?, ?)",
                (1001, "Comprador A", "hu14a@example.com", "hash-de-prueba"),
            )
            conexion.execute(
                "INSERT INTO usuarios (id, nombre_completo, correo, contrasena_hash) VALUES (?, ?, ?, ?)",
                (1002, "Comprador B", "hu14b@example.com", "hash-de-prueba"),
            )

    def limpiar_temporal(self):
        # SQLite puede retener cursores hasta la recolección de basura en Windows.
        gc.collect()
        self.temporal.cleanup()

    def test_01_inicialmente_no_autorizado(self):
        self.assertEqual(service.consultar_consentimiento(1001), {
            "autorizado": False, "actualizado_en": None,
        })
        self.assertFalse(service.tiene_autorizacion(1001))

    def test_02_aceptacion_persistida(self):
        guardado = service.guardar_consentimiento(1001, True)
        self.assertTrue(guardado["autorizado"])
        self.assertIsNotNone(guardado["actualizado_en"])
        self.assertTrue(service.tiene_autorizacion(1001))
        self.assertTrue(service.consultar_consentimiento(1001)["autorizado"])

    def test_03_rechazo_revoca_autorizacion(self):
        service.guardar_consentimiento(1001, True)
        service.guardar_consentimiento(1001, False)
        self.assertFalse(service.tiene_autorizacion(1001))

    def test_04_consentimiento_individual(self):
        service.guardar_consentimiento(1001, True)
        self.assertFalse(service.tiene_autorizacion(1002))
        service.guardar_consentimiento(1002, False)
        self.assertTrue(service.tiene_autorizacion(1001))

    def test_05_rechazar_datos_no_booleanos(self):
        with self.assertRaises(ValueError):
            service.guardar_consentimiento(1001, "sí")


if __name__ == "__main__":
    unittest.main()

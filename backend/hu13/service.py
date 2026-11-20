from hu11 import repository


def listar_usuarios() -> list[dict]:
    repository.inicializar_base_datos()
    with repository.conectar() as conexion:
        filas = conexion.execute(
            "SELECT id, nombre_completo, correo, activo, rol "
            "FROM usuarios ORDER BY id"
        ).fetchall()
    return [
        {**dict(fila), "activo": bool(fila["activo"])}
        for fila in filas
    ]


def actualizar_usuario(usuario_id: int, cambios: dict) -> dict | None:
    if not cambios:
        return None
    repository.inicializar_base_datos()
    campos = []
    valores = []
    for campo in ("activo", "rol"):
        if campo in cambios:
            campos.append(f"{campo} = ?")
            valor = cambios[campo]
            valores.append(int(valor) if campo == "activo" else valor)
    with repository.conectar() as conexion:
        cursor = conexion.execute(
            f"UPDATE usuarios SET {', '.join(campos)} WHERE id = ?",
            (*valores, usuario_id),
        )
        if cursor.rowcount == 0:
            return None
        fila = conexion.execute(
            "SELECT id, nombre_completo, correo, activo, rol "
            "FROM usuarios WHERE id = ?",
            (usuario_id,),
        ).fetchone()
    return {**dict(fila), "activo": bool(fila["activo"])}

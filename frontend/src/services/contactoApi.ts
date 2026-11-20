
export interface DatosContacto {
  nombre_completo: string
  telefono: string
  correo: string | null
}

export interface RespuestaContacto {
  mensaje: string
  solicitud_id: string
  producto_id: number
  estado: string
  contacto: DatosContacto
}

export async function guardarContacto(
  solicitudId: string,
  datos: DatosContacto
): Promise<RespuestaContacto> {
  const respuesta = await fetch(
    `http://127.0.0.1:8000/api/solicitudes/${encodeURIComponent(solicitudId)}/contacto`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(datos),
    }
  )

  if (!respuesta.ok) {
    if (respuesta.status === 422) {
      throw new Error('Revisa los datos obligatorios del formulario.')
    }
    if (respuesta.status === 404) {
      throw new Error('No se encontró la solicitud.')
    }
    throw new Error('No fue posible guardar los datos de contacto.')
  }

  return (await respuesta.json()) as RespuestaContacto
}

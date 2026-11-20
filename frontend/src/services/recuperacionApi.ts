const API_URL = 'http://127.0.0.1:8000'

async function procesarRespuesta(respuesta: Response): Promise<string> {
  let contenido: { mensaje?: string; detail?: string } = {}
  try {
    contenido = (await respuesta.json()) as typeof contenido
  } catch {
    // Mensaje predeterminado en caso de respuesta no JSON.
  }

  if (!respuesta.ok) {
    throw new Error(
      typeof contenido.detail === 'string'
        ? contenido.detail
        : 'No fue posible completar la operación. Inténtalo nuevamente.'
    )
  }

  return contenido.mensaje ?? 'Operación realizada.'
}

export async function solicitarRecuperacion(correo: string): Promise<string> {
  const respuesta = await fetch(`${API_URL}/api/auth/recuperar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ correo }),
  })
  return procesarRespuesta(respuesta)
}

export async function restablecerContrasena(
  token: string,
  nuevaContrasena: string
): Promise<string> {
  const respuesta = await fetch(`${API_URL}/api/auth/restablecer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, nueva_contrasena: nuevaContrasena }),
  })
  return procesarRespuesta(respuesta)
}

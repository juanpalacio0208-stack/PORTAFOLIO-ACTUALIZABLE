
import { useState } from 'react'
import { guardarContacto } from '../services/contactoApi'
import type { DatosContacto } from '../services/contactoApi'
import '../contacto.css'

interface Props {
  solicitudId: string
  productoNombre: string
  volver: () => void
}

function ContactoCompradorPage({
  solicitudId,
  productoNombre,
  volver,
}: Props) {
  const [nombre, setNombre] = useState('')
  const [telefono, setTelefono] = useState('')
  const [correo, setCorreo] = useState('')
  const [errores, setErrores] = useState<Record<string, string>>({})
  const [guardando, setGuardando] = useState(false)
  const [completado, setCompletado] = useState(false)
  const [errorGeneral, setErrorGeneral] = useState('')

  function validar(): Record<string, string> {
    const nuevosErrores: Record<string, string> = {}

    if (nombre.trim().length < 3) {
      nuevosErrores.nombre = 'Ingresa tu nombre completo (mínimo 3 caracteres).'
    }

    if (!/^\+?\d{10,15}$/.test(telefono.trim())) {
      nuevosErrores.telefono = 'Ingresa un teléfono válido de 10 a 15 dígitos.'
    }

    if (
      correo.trim() &&
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo.trim())
    ) {
      nuevosErrores.correo = 'Ingresa un correo electrónico válido.'
    }

    return nuevosErrores
  }

  async function manejarEnvio(evento: React.FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    const nuevosErrores = validar()
    setErrores(nuevosErrores)
    setErrorGeneral('')

    if (Object.keys(nuevosErrores).length > 0) return

    const datos: DatosContacto = {
      nombre_completo: nombre.trim(),
      telefono: telefono.trim(),
      correo: correo.trim() || null,
    }

    setGuardando(true)

    try {
      await guardarContacto(solicitudId, datos)
      setCompletado(true)
    } catch (error) {
      setErrorGeneral(
        error instanceof Error ? error.message : 'Ocurrió un error.'
      )
    } finally {
      setGuardando(false)
    }
  }

  if (completado) {
    return (
      <main className="contacto-contenedor">
        <section className="contacto-tarjeta" role="status">
          <h1>¡Datos guardados correctamente!</h1>
          <p>Tu solicitud del producto <strong>{productoNombre}</strong> tiene los datos de contacto completos.</p>
          <p>Ya está preparada para continuar mediante WhatsApp en HU-10.</p>
          <button type="button" onClick={volver}>
            Volver al producto
          </button>
        </section>
      </main>
    )
  }

  return (
    <main className="contacto-contenedor">
      <section className="contacto-tarjeta">
        <button type="button" onClick={volver} className="contacto-volver">
          ← Volver al producto
        </button>

        <h1>Información de contacto</h1>
        <p>Completa tus datos para continuar tu solicitud con Laura.</p>
        <p><strong>Producto:</strong> {productoNombre}</p>

        <form onSubmit={(evento) => void manejarEnvio(evento)} noValidate>
          <label htmlFor="nombre">Nombre completo *</label>
          <input id="nombre" value={nombre} onChange={(e) => setNombre(e.target.value)}
            aria-invalid={Boolean(errores.nombre)} />
          {errores.nombre && <p role="alert">{errores.nombre}</p>}

          <label htmlFor="telefono">Teléfono / WhatsApp *</label>
          <input id="telefono" type="tel" value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
            aria-invalid={Boolean(errores.telefono)} />
          {errores.telefono && <p role="alert">{errores.telefono}</p>}

          <label htmlFor="correo">Correo electrónico (opcional)</label>
          <input id="correo" type="email" value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            aria-invalid={Boolean(errores.correo)} />
          {errores.correo && <p role="alert">{errores.correo}</p>}

          {errorGeneral && <p role="alert">{errorGeneral}</p>}

          <button type="submit" disabled={guardando}>
            {guardando ? 'Guardando...' : 'Guardar y continuar'}
          </button>
        </form>
      </section>
    </main>
  )
}

export default ContactoCompradorPage

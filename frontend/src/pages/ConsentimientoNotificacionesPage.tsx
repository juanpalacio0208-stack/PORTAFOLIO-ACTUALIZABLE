import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import {
  consultarConsentimiento,
  guardarConsentimiento,
} from '../services/consentimientoApi'
import '../consentimiento.css'

interface Props {
  volver: () => void
}

type Eleccion = 'aceptar' | 'rechazar'

export default function ConsentimientoNotificacionesPage({ volver }: Props) {
  const [eleccion, setEleccion] = useState<Eleccion>('rechazar')
  const [cargando, setCargando] = useState(true)
  const [guardando, setGuardando] = useState(false)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [guardado, setGuardado] = useState<boolean | null>(null)

  useEffect(() => {
    let vigente = true
    consultarConsentimiento()
      .then((datos) => {
        if (!vigente) return
        setEleccion(datos.autorizado ? 'aceptar' : 'rechazar')
        setGuardado(datos.autorizado)
      })
      .catch((err: unknown) => {
        if (vigente) setError(err instanceof Error ? err.message : 'Error de conexión.')
      })
      .finally(() => {
        if (vigente) setCargando(false)
      })
    return () => { vigente = false }
  }, [])

  async function manejarGuardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError('')
    setMensaje('')
    setGuardando(true)
    try {
      const datos = await guardarConsentimiento(eleccion === 'aceptar')
      setGuardado(datos.autorizado)
      setMensaje(datos.autorizado
        ? 'Has autorizado las notificaciones promocionales.'
        : 'Has rechazado o revocado las notificaciones promocionales.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo guardar.')
    } finally {
      setGuardando(false)
    }
  }

  return (
    <main className="hu14-fondo">
      <section className="hu14-panel">
        <button className="hu14-volver" type="button" onClick={volver}>
          ← Volver a mi cuenta
        </button>
        <span className="hu14-etiqueta">PREFERENCIAS DE COMUNICACIÓN</span>
        <h1>Autorizar notificaciones</h1>
        <p className="hu14-descripcion">
          Decide si deseas recibir novedades, anuncios y promociones del portafolio.
          Tu autorización es voluntaria y puedes cambiarla cuando quieras.
        </p>

        {cargando ? <p role="status">Consultando tus preferencias...</p> : (
          <form onSubmit={(evento) => void manejarGuardar(evento)}>
            <fieldset className="hu14-opciones" disabled={guardando}>
              <legend>¿Autorizas las notificaciones promocionales?</legend>
              <label className={`hu14-opcion ${eleccion === 'aceptar' ? 'seleccionada' : ''}`}>
                <input type="radio" name="consentimiento" value="aceptar"
                  checked={eleccion === 'aceptar'}
                  onChange={() => { setEleccion('aceptar'); setMensaje('') }} />
                <span><strong>Sí, autorizo</strong><small>Quiero recibir novedades y promociones.</small></span>
              </label>
              <label className={`hu14-opcion ${eleccion === 'rechazar' ? 'seleccionada' : ''}`}>
                <input type="radio" name="consentimiento" value="rechazar"
                  checked={eleccion === 'rechazar'}
                  onChange={() => { setEleccion('rechazar'); setMensaje('') }} />
                <span><strong>No autorizo</strong><small>No recibiré notificaciones promocionales.</small></span>
              </label>
            </fieldset>
            {guardado !== null && (
              <p className="hu14-estado">Preferencia guardada: <strong>{guardado ? 'Autorizada' : 'No autorizada'}</strong></p>
            )}
            <button className="hu14-guardar" type="submit" disabled={guardando}>
              {guardando ? 'Guardando...' : 'Guardar preferencias'}
            </button>
          </form>
        )}
        {error && <p role="alert" className="hu14-error">{error}</p>}
        {mensaje && <p role="status" className="hu14-exito">{mensaje}</p>}
        <p className="hu14-nota">No se enviarán promociones sin tu autorización registrada.</p>
      </section>
    </main>
  )
}

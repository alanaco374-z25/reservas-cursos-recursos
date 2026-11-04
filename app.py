import json
import os
import smtplib
import urllib.request
from contextlib import closing
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
import psycopg2
from psycopg2.errors import UniqueViolation
from psycopg2.extras import RealDictCursor
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
CLAVE_CANCELACION = os.getenv("CLAVE_CANCELACION", "")
EMAIL_SERVIDOR = os.getenv("EMAIL_SERVIDOR", "").strip()
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "").strip()

AULAS_RECURSOS = [
    "Notebooks",
    "Equipo de Sonido Grande",
    "Parlante Chico",
    "Laboratorio",
    "Salón de Usos Múltiples (SUM)",
    "Proyector Móvil A",
    "Sala de Informatica",
    "Tablets",
]

TURNOS = [
    "07:00 AM - 08:20 AM (Módulos 1 y 2 - Mañana)",
    "08:30 AM - 09:50 AM (Módulos 3 y 4 - Mañana)",
    "10:00 AM - 11:20 AM (Módulos 5 y 6 - Mañana)",
    "11:20 AM - 12:00 PM (Módulos 7 y 8 - Mañana)",
    "12:00 PM - 12:40 PM (Módulo 9 Final - Mañana)",
    "01:00 PM - 02:20 PM (Módulos 1 y 2 - Tarde)",
    "02:30 PM - 03:50 PM (Módulos 3 y 4 - Tarde)",
    "04:00 PM - 05:20 PM (Módulos 5 y 6 - Tarde)",
    "05:20 PM - 06:00 PM (Módulos 7 y 8 - Tarde)",
    "06:00 PM - 06:40 PM (Módulo 9 Final - Tarde)",
]


def conectar_db():
    if not DATABASE_URL:
        raise RuntimeError("Falta configurar DATABASE_URL.")
    return psycopg2.connect(DATABASE_URL, sslmode="require", connect_timeout=10)


def enviar_correo_confirmacion(destinatario, reserva):
    print("--- INICIANDO ENVÍO DE CORREO (SMTP GMAIL) ---")
    print(f"Destinatario: {destinatario}")
    
    if not EMAIL_SERVIDOR or not EMAIL_PASSWORD:
        print("ERROR: Faltan las credenciales de correo (EMAIL_SERVIDOR o EMAIL_PASSWORD).")
        return False
    if not destinatario:
        print("ERROR: No se proporcionó correo de destinatario.")
        return False

    html_contenido = f"""
    <div style="font-family: Arial, sans-serif; color: #333; padding: 20px; border: 1px solid #E6C653; border-radius: 10px;">
        <h2 style="color: #2C3E50;">Instituto Inmaculada Concepción</h2>
        <h3 style="color: #D4AC0D;">Confirmación de Reserva de Recurso</h3>
        <p>Estimado/a <b>{reserva['profesor']}</b>,</p>
        <p>Su solicitud ha sido registrada con éxito en el sistema digital.</p>
        <hr style="border: 0; border-top: 1px solid #eee;">
        <ul>
            <li><b>Recurso / Espacio:</b> {reserva['recurso']}</li>
            <li><b>Fecha:</b> {reserva['fecha']}</li>
            <li><b>Bloque Horario:</b> {reserva['turno']}</li>
            <li><b>Estado:</b> {reserva.get('estado', 'SOLICITADO')}</li>
        </ul>
        <p style="font-size: 0.9em; color: #7f8c8d;">Este es un mensaje automático del sistema de reservas escolares.</p>
    </div>
    """

    mensaje = MIMEMultipart("alternative")
    mensaje["Subject"] = f"Reserva Confirmada: {reserva['recurso']} ({reserva['fecha']})"
    mensaje["From"] = f"Sistema de Reservas IIC <{EMAIL_SERVIDOR}>"
    mensaje["To"] = destinatario

    mensaje.attach(MIMEText(html_contenido, "html"))

    try:
        # Definimos un timeout de 7 segundos para que la app nunca se quede congelada
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=7) as servidor:
            servidor.starttls()
            servidor.login(EMAIL_SERVIDOR, EMAIL_PASSWORD)
            servidor.sendmail(EMAIL_SERVIDOR, destinatario, mensaje.as_string())
        print(f"ÉXITO SMTP: Correo enviado correctamente a {destinatario}")
        return True
    except Exception as e:
        print(f"ERROR SMTP GENERAL (Controlado): {e}")
        return False


def cargar_reservas():
    consulta = """
        SELECT id, profesor, email,
               TO_CHAR(fecha, 'YYYY-MM-DD') AS fecha,
               recurso, turno,
               TO_CHAR(registro AT TIME ZONE 'America/Argentina/Buenos_Aires', 'DD/MM/YYYY HH24:MI') AS registro
        FROM public.reservas
        ORDER BY fecha, turno, id
    """
    with closing(conectar_db()) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(consulta)
            reservas = [dict(fila) for fila in cur.fetchall()]
    for reserva in reservas:
        reserva["estado"] = "SOLICITADO"
    return reservas


def guardar_reserva(reserva):
    consulta = """
        INSERT INTO public.reservas (profesor, email, fecha, recurso, turno)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id,
                  TO_CHAR(fecha, 'YYYY-MM-DD') AS fecha,
                  TO_CHAR(registro AT TIME ZONE 'America/Argentina/Buenos_Aires', 'DD/MM/YYYY HH24:MI') AS registro
    """
    with closing(conectar_db()) as conn:
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        consulta,
                        (
                            reserva["profesor"],
                            reserva["email"],
                            reserva["fecha"],
                            reserva["recurso"],
                            reserva["turno"],
                        ),
                    )
                    guardada = dict(cur.fetchone())
            reserva.update(guardada)
            return reserva
        except UniqueViolation:
            return None


def eliminar_reserva(reserva_id):
    with closing(conectar_db()) as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM public.reservas WHERE id = %s", (reserva_id,)
                )
                return cur.rowcount == 1


st.set_page_config(
    page_title="Reserva de Recursos - IIC", page_icon="🏫", layout="centered"
)

st.markdown(
    """
    <div style='text-align: center; padding: 10px; border-bottom: 2px solid #E6C653; margin-bottom: 25px;'>
        <h1 style='color: #E6C653; margin-bottom: 0px; font-weight: 600; font-size: 2.2rem;'>INSTITUTO INMACULADA CONCEPCIÓN</h1>
        <p style='color: #8D99AE; letter-spacing: 2px; font-size: 0.9rem; margin-top: 5px;'>SISTEMA DIGITAL DE RESERVAS PARA DOCENTES</p>
    </div>
""",
    unsafe_allow_html=True,
)

try:
    reservas_actuales = cargar_reservas()
except Exception as error:
    st.error(
        "No se pudo conectar con la base de datos de reservas de Supabase."
    )
    st.caption(
        "Revisá que DATABASE_URL esté configurada correctamente y que la tabla public.reservas exista."
    )
    st.exception(error)
    st.stop()

if "reserva_confirmada" in st.session_state:
    reserva_confirmada = st.session_state.pop("reserva_confirmada")
    st.success(
        "🎉 ¡Reserva realizada con éxito! Tu solicitud ya quedó registrada y se envió un correo de confirmación."
    )
    st.info(
        f"**Estado:** {reserva_confirmada.get('estado', 'SOLICITADO')}\n\n"
        f"**Recurso:** {reserva_confirmada['recurso']}\n\n"
        f"**Fecha:** {reserva_confirmada['fecha']}\n\n"
        f"**Horario:** {reserva_confirmada['turno']}\n\n"
        f"**Docente:** {reserva_confirmada['profesor']}"
    )
    st.balloons()

tab_nueva, tab_planilla, tab_cancelar = st.tabs(
    ["📝 Nueva Reserva", "📋 Planilla y Disponibilidad", "❌ Cancelar Reserva"]
)

with tab_nueva:
    st.markdown(
        "<h3 style='color: #E6C653; font-size: 1.3rem;'>Registrar Asignación de Espacio</h3>",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        nombre_profesor = st.text_input("Nombre y Apellido del Docente:")
        email_profesor = st.text_input(
            "Correo Electrónico (para recibir la confirmación):"
        )
        col1, col2 = st.columns(2)
        with col1:
            fecha_seleccionada = st.date_input(
                "Fecha:", min_value=datetime.today().date()
            )
            fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")
        with col2:
            recurso_seleccionado = st.selectbox(
                "Aula o Recurso requerido:", AULAS_RECURSOS
            )
        turno_seleccionado = st.selectbox("Bloque Horario Escolar:", TURNOS)
        es_fin_de_semana = fecha_seleccionada.weekday() in [5, 6]

    if es_fin_de_semana:
        st.error(
            "🔒 El establecimiento se encuentra cerrado los fines de semana. Seleccione días de Lunes a Viernes."
        )
    elif st.button(
        "Confirmar y Bloquear Horario", type="primary", use_container_width=True
    ):
        if not nombre_profesor.strip():
            st.toast("⚠️ Complete su nombre para continuar.", icon="👤")
        elif not email_profesor.strip() or "@" not in email_profesor:
            st.toast(
                "⚠️ Ingrese un correo electrónico válido para la confirmación.",
                icon="📧",
            )
        else:
            nueva_reserva = {
                "profesor": nombre_profesor.strip().title(),
                "email": email_profesor.strip().lower(),
                "fecha": fecha_str,
                "recurso": recurso_seleccionado,
                "turno": turno_seleccionado,
                "estado": "SOLICITADO",
            }
            try:
                guardada = guardar_reserva(nueva_reserva)
                if guardada is None:
                    existentes = cargar_reservas()
                    ocupante = next(
                        (
                            r["profesor"]
                            for r in existentes
                            if r["fecha"] == fecha_str
                            and r["recurso"] == recurso_seleccionado
                            and r["turno"] == turno_seleccionado
                        ),
                        "otro docente",
                    )
                    st.error(
                        f"❌ **Conflicto de reserva:** El espacio ya fue asignado al/la Prof. {ocupante} para este día y horario."
                    )
                else:
                    enviar_correo_confirmacion(email_profesor.strip().lower(), guardada)
                    st.session_state["reserva_confirmada"] = guardada
                    st.rerun()
            except Exception as error:
                st.error("No se pudo guardar la reserva en Supabase.")
                st.exception(error)

with tab_planilla:
    st.markdown(
        "<h3 style='color: #E6C653; font-size: 1.3rem;'>Planilla de Ocupación General</h3>",
        unsafe_allow_html=True,
    )
    if not reservas_actuales:
        st.info("No se registran turnos ocupados en el sistema actual.")
    else:
        df = pd.DataFrame(reservas_actuales)
        df_visualizacion = df.rename(
            columns={
                "fecha": "Fecha",
                "recurso": "Espacio / Recurso",
                "turno": "Bloque Horario",
                "profesor": "Docente a Cargo",
                "email": "Correo",
                "registro": "Alta en Sistema",
                "estado": "Estado",
            }
        )
        if "Estado" not in df_visualizacion.columns:
            df_visualizacion["Estado"] = "SOLICITADO"
        else:
            df_visualizacion["Estado"] = df_visualizacion["Estado"].fillna(
                "SOLICITADO"
            )
        df_visualizacion = df_visualizacion.sort_values(by="Fecha")
        columnas_ordenadas = [
            "Fecha",
            "Espacio / Recurso",
            "Bloque Horario",
            "Docente a Cargo",
            "Correo",
            "Estado",
            "Alta en Sistema",
        ]
        df_visualizacion = df_visualizacion[columnas_ordenadas]
        with st.expander("🔍 Herramientas de filtrado y búsqueda"):
            busqueda = st.text_input(
                "Filtrar por apellido del docente o aula específica:"
            )
            if busqueda:
                df_visualizacion = df_visualizacion[
                    df_visualizacion.astype(str)
                    .apply(
                        lambda x: x.str.contains(busqueda, case=False, na=False)
                    )
                    .any(axis=1)
                ]
        st.dataframe(df_visualizacion, use_container_width=True, hide_index=True)
        csv = df_visualizacion.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 Descargar Reporte Completo (CSV)",
            data=csv,
            file_name=f"reservas_inmaculada_{datetime.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

with tab_cancelar:
    st.markdown(
        "<h3 style='color: #E6C653; font-size: 1.3rem;'>Anulación de Turnos Asignados</h3>",
        unsafe_allow_html=True,
    )
    if not reservas_actuales:
        st.info("No hay reservas registradas en el sistema para poder cancelar.")
    else:
        st.write("Seleccioná la reserva que deseas eliminar del sistema:")
        opciones = {
            r["id"]: f"{r['fecha']} | {r['recurso']} | {r['turno']} (Prof. {r['profesor']})"
            for r in reservas_actuales
        }
        reserva_id = st.selectbox(
            "Seleccionar turno a dar de baja:",
            options=list(opciones.keys()),
            format_func=lambda reserva_id: opciones[reserva_id],
        )
        with st.container(border=True):
            clave_ingresada = st.text_input(
                "Ingresar Clave de Seguridad Institucional:", type="password"
            )
        if st.button(
            "Proceder a la Eliminación", type="primary", use_container_width=True
        ):
            if not CLAVE_CANCELACION:
                st.error(
                    "Falta configurar CLAVE_CANCELACION en las variables de entorno."
                )
            elif clave_ingresada == CLAVE_CANCELACION:
                seleccionada = next(
                    r for r in reservas_actuales if r["id"] == reserva_id
                )
                try:
                    if eliminar_reserva(reserva_id):
                        st.toast(
                            f"Se eliminó con éxito el turno de {seleccionada['recurso']}.",
                            icon="🗑️",
                        )
                        st.success(
                            f"✅ La reserva de **{seleccionada['recurso']}** para el día **{seleccionada['fecha']}** ha sido removida del sistema."
                        )
                        st.rerun()
                    else:
                        st.error(
                            "La reserva ya no existe. Actualizá la página e intentá nuevamente."
                        )
                except Exception as error:
                    st.error("No se pudo eliminar la reserva de Supabase.")
                    st.exception(error)
            elif not clave_ingresada:
                st.toast(
                    "⚠️ Por favor, introduzca la clave de seguridad.", icon="🔑"
                )
            else:
                st.error(
                    "🔒 Clave incorrecta. No tiene los permisos requeridos para modificar la planilla escolar."
                )
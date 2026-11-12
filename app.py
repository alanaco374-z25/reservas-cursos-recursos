import streamlit as st  
import json  
import os  
from datetime import datetime  
import pandas as pd  
import base64

# Configuración y almacenamiento de datos  
DB_FILE = "reservas.json"  
CLAVE_CANCELACION = "Inmaculada2026"   

# Diccionario de recursos con sus respectivas descripciones e imágenes ilustrativas de alta calidad
AULAS_RECURSOS = {
    "Notebooks": {
        "cat": "Equipamiento Informático",
        "desc": "Carro móvil con notebooks para uso digital en aulas.",
        "img": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80"
    },
    "Equipo de Sonido Grande": {
        "cat": "Multimedia",
        "desc": "Sistema de audio potenciado para actos y eventos masivos.",
        "img": "https://images.unsplash.com/photo-1545128485-c400e7702796?auto=format&fit=crop&w=600&q=80"
    },
    "Equipo de Sonido Chico": {
        "cat": "Multimedia",
        "desc": "Bafle portátil con micrófono para clases y charlas.",
        "img": "https://images.unsplash.com/photo-1520523839891-508fc8269d67?auto=format&fit=crop&w=600&q=80"
    },
    "Laboratorio": {
        "cat": "Espacios Académicos",
        "desc": "Espacio equipado para prácticas de ciencias y química.",
        "img": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=600&q=80"
    },
    "Salón de Usos Múltiples (SUM)": {
        "cat": "Espacios Académicos",
        "desc": "Salón amplio para reuniones, educación física y eventos.",
        "img": "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?auto=format&fit=crop&w=600&q=80"
    },
    "Proyector Móvil A": {
        "cat": "Multimedia",
        "desc": "Cañón proyector multimedia de alta definición.",
        "img": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=600&q=80"
    },
    "Biblioteca": {
        "cat": "Espacios Académicos",
        "desc": "Área silenciosa de lectura, consulta e investigación.",
        "img": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=600&q=80"
    },
    "Tablets": {
        "cat": "Equipamiento Informático",
        "desc": "Set de tablets digitales educativas para estudiantes.",
        "img": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=600&q=80"
    }
}

TURNOS = [  
    # --- TURNO MAÑANA ---  
    "07:00 AM - 08:20 AM (Módulos 1 y 2 - Mañana)",  
    "08:30 AM - 09:50 AM (Módulos 3 y 4 - Mañana)",  
    "10:00 AM - 11:20 AM (Módulos 5 y 6 - Mañana)",  
    "11:20 AM - 12:00 PM (Módulos 7 y 8 - Mañana)",  
    "12:00 PM - 12:40 PM (Módulo 9 Final - Mañana)",  
    # --- TURNO TARDE ---  
    "01:00 PM - 02:20 PM (Módulos 1 y 2 - Tarde)",  
    "02:30 PM - 03:50 PM (Módulos 3 y 4 - Tarde)",  
    "04:00 PM - 05:20 PM (Módulos 5 y 6 - Tarde)",  
    "05:20 PM - 06:00 PM (Módulos 7 y 8 - Tarde)",  
    "06:00 PM - 06:40 PM (Módulo 9 Final - Tarde)"  
]  

def cargar_reservas():  
    if os.path.exists(DB_FILE):  
        with open(DB_FILE, "r", encoding="utf-8") as f:  
            try: return json.load(f)  
            except json.JSONDecodeError: return []  
    return []  

def guardar_reservas(reservas):  
    with open(DB_FILE, "w", encoding="utf-8") as f:  
        json.dump(reservas, f, ensure_ascii=False, indent=4)  

# Configuración de página  
st.set_page_config(page_title="Gestión de Espacios - IIC", page_icon="🏫", layout="centered")  

# Estilos CSS personalizados para máxima elegancia, tipografías refinadas y tarjetas visuales
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="st"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0b1c3c 0%, #172d55 100%);
        padding: 30px 20px;
        border-radius: 16px;
        text-align: center;
        border-bottom: 4px solid #E6C653;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        margin-bottom: 30px;
    }
    
    .resource-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        transition: transform 0.2s ease;
    }
    .resource-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(230, 198, 83, 0.15);
        border-color: #E6C653;
    }
</style>
""", unsafe_allow_html=True)

reservas_actuales = cargar_reservas()  

# --- ENCABEZADO INSTITUCIONAL CON LOGOTIPO ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    if os.path.exists("LOGO.png"):
        st.image("LOGO.png", width=95)
    else:
        st.write("🏫")

with col_titulo:
    st.markdown("""
        <div style='padding-top: 5px;'>
            <h2 style='color: #0b1c3c; margin: 0px; font-weight: 700; font-size: 1.8rem; letter-spacing: -0.5px;'>INSTITUTO INMACULADA CONCEPCIÓN</h2>
            <p style='color: #556987; font-weight: 500; font-size: 0.95rem; margin-top: 4px;'>Sistema Digital de Gestión y Reserva de Espacios Académicos</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 20px; margin-bottom: 25px; border: 0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

# --- NAVEGACIÓN POR PESTAÑAS ---  
tab_nueva, tab_recursos, tab_planilla, tab_cancelar = st.tabs(["📝 Nueva Reserva", "🖼️ Catálogo Visual", "📊 Planilla y Disponibilidad", "❌ Cancelar Reserva"])  

# ==========================================  
# PESTAÑA 1: NUEVA RESERVA  
# ==========================================  
with tab_nueva:  
    st.markdown("<h4 style='color: #0b1c3c; font-weight: 600; margin-bottom: 15px;'>Registrar Solicitud de Recurso</h4>", unsafe_allow_html=True)  
    
    with st.container(border=True):  
        nombre_profesor = st.text_input("Nombre y Apellido del Docente:")  
        
        col1, col2 = st.columns(2)  
        with col1:  
            fecha_seleccionada = st.date_input("Fecha de reserva:", min_value=datetime.today())  
            fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")  
        with col2:  
            recurso_seleccionado = st.selectbox("Seleccione Aula o Recurso:", list(AULAS_RECURSOS.keys()))  
        
        # Tarjeta previa del recurso seleccionado con su foto
        info_recurso = AULAS_RECURSOS[recurso_seleccionado]
        st.markdown(f"""
            <div style="display: flex; align-items: center; background: #f8fafc; padding: 12px; border-radius: 10px; border-left: 4px solid #0b1c3c; margin: 15px 0;">
                <img src="{info_recurso['img']}" style="width: 70px; height: 50px; object-fit: cover; border-radius: 6px; margin-right: 15px;">
                <div>
                    <span style="font-size: 0.75rem; color: #E6C653; font-weight: 700; text-transform: uppercase;">{info_recurso['cat']}</span>
                    <p style="margin: 0; font-size: 0.9rem; color: #334155; font-weight: 500;">{info_recurso['desc']}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        turno_seleccionado = st.selectbox("Bloque Horario Escolar:", TURNOS)  
        
        es_fin_de_semana = fecha_seleccionada.weekday() in [5, 6]  
        
        if es_fin_de_semana:  
            st.error("🔒 El establecimiento permanece cerrado los fines de semana. Seleccione un día hábil (Lunes a Viernes).")  
        else:  
            if st.button("Confirmar y Bloquear Horario", type="primary", use_container_width=True):  
                if not nombre_profesor.strip():  
                    st.toast("⚠️ Complete su nombre y apellido para continuar.", icon="👤")  
                else:  
                    conflicto = False  
                    for r in reservas_actuales:  
                        if (r["fecha"] == fecha_str and r["recurso"] == recurso_seleccionado and r["turno"] == turno_seleccionado):  
                            conflicto = True  
                            profesor_ocupante = r["profesor"]  
                            break  
                    
                    if conflicto:  
                        st.error(f"❌ **Conflicto de reserva:** El espacio ya se encuentra asignado al/la Prof. {profesor_ocupante} para este día y bloque horario.")  
                    else:  
                        nueva_reserva = {  
                            "profesor": nombre_profesor.strip().title(),  
                            "fecha": fecha_str,  
                            "recurso": recurso_seleccionado,  
                            "turno": turno_seleccionado,  
                            "registro": datetime.now().strftime("%d/%m/%Y %H:%M")  
                        }  
                        reservas_actuales.append(nueva_reserva)  
                        guardar_reservas(reservas_actuales)  
                        st.success(f"✅ ¡Reserva registrada con éxito! **{recurso_seleccionado}** asignado correctamente.")  
                        st.balloons()  
                        st.rerun()  

# ==========================================  
# PESTAÑA 2: CATÁLOGO VISUAL DE RECURSOS  
# ==========================================
with tab_recursos:
    st.markdown("<h4 style='color: #0b1c3c; font-weight: 600; margin-bottom: 15px;'>Galería de Espacios y Equipamiento Institucional</h4>", unsafe_allow_html=True)
    st.write("Conozca en detalle los recursos disponibles para las actividades pedagógicas:")
    
    cols = st.columns(2)
    idx = 0
    for nombre, datos in AULAS_RECURSOS.items():
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="resource-card">
                    <img src="{datos['img']}" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">
                    <h4 style="margin: 5px 0; color: #0b1c3c; font-size: 1.05rem;">{nombre}</h4>
                    <p style="font-size: 0.75rem; color: #d97706; font-weight: 700; margin-bottom: 5px;">{datos['cat']}</p>
                    <p style="font-size: 0.85_rem; color: #64748b; margin-bottom: 0;">{datos['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
            st.write("") # Espaciador
        idx += 1

# ==========================================  
# PESTAÑA 3: PLANILLA Y DISPONIBILIDAD  
# ==========================================  
with tab_planilla:  
    st.markdown("<h4 style='color: #0b1c3c; font-weight: 600; margin-bottom: 15px;'>Planilla General de Ocupación</h4>", unsafe_allow_html=True)  
    
    if not reservas_actuales:  
        st.info("No se registran turnos ocupados en el sistema actualmente.")  
    else:  
        df = pd.DataFrame(reservas_actuales)  
        df_visualizacion = df.rename(columns={  
            "fecha": "Fecha", "recurso": "Espacio / Recurso",  
            "turno": "Bloque Horario", "profesor": "Docente a Cargo",  
            "registro": "Alta en Sistema"  
        })  
        
        df_visualizacion = df_visualizacion.sort_values(by="Fecha")  
        columnas_ordenadas = ["Fecha", "Espacio / Recurso", "Bloque Horario", "Docente a Cargo", "Alta en Sistema"]  
        df_visualizacion = df_visualizacion[columnas_ordenadas]  
        
        with st.expander("🔍 Herramientas de filtrado y búsqueda rápida"):  
            busqueda = st.text_input("Filtrar por docente o recurso específico:")  
            if busqueda:  
                df_visualizacion = df_visualizacion[  
                    df_visualizacion.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)  
                ]  
        
        st.dataframe(  
            df_visualizacion,  
            use_container_width=True,  
            hide_index=True  
        )  
        
        csv = df_visualizacion.to_csv(index=False).encode('utf-8')  
        st.download_button(  
            label="📥 Descargar Reporte Escolar (CSV)",  
            data=csv,  
            file_name=f"reservas_inmaculada_{datetime.today().strftime('%Y%m%d')}.csv",  
            mime="text/csv",  
            use_container_width=True  
        )  

# ==========================================  
# PESTAÑA 4: CANCELAR RESERVA  
# ==========================================  
with tab_cancelar:  
    st.markdown("<h4 style='color: #0b1c3c; font-weight: 600; margin-bottom: 15px;'>Anulación de Turnos Asignados</h4>", unsafe_allow_html=True)  
    
    if not reservas_actuales:  
        st.info("No hay reservas registradas en el sistema para poder cancelar.")  
    else:  
        st.write("Seleccione el turno que desea eliminar de la base de datos:")  
        
        opciones_cancelar = []  
        for i, r in enumerate(reservas_actuales):  
            texto_reserva = f"{r['fecha']} | {r['recurso']} | {r['turno']} (Prof. {r['profesor']})"  
            opciones_cancelar.append((i, texto_reserva))  
        
        reserva_a_eliminar_idx = st.selectbox(  
            "Seleccionar turno a dar de baja:",  
            options=[opt[0] for opt in opciones_cancelar],  
            format_func=lambda x: next(opt[1] for opt in opciones_cancelar if opt[0] == x)  
        )  
        
        with st.container(border=True):  
            clave_ingresada = st.text_input("Ingresar Clave de Seguridad Institucional:", type="password")  
            
            if st.button("Proceder a la Eliminación", type="primary", use_container_width=True):  
                if clave_ingresada == CLAVE_CANCELACION:  
                    eliminada = reservas_actuales.pop(reserva_a_eliminar_idx)  
                    guardar_reservas(reservas_actuales)  
                    
                    st.toast(f"Se eliminó con éxito el turno de {eliminada['recurso']}.", icon="🗑️")  
                    st.success(f"✅ La reserva de **{eliminada['recurso']}** para el día **{eliminada['fecha']}** ha sido removida del sistema.")  
                    st.rerun()  
                elif not clave_ingresada:  
                    st.toast("⚠️ Por favor, introduzca la clave de seguridad.", icon="🔑")  
                else:  
                    st.error("🔒 Clave incorrecta. No tiene los permisos requeridos para modificar la agenda.")

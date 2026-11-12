import streamlit as st  
import json  
import os  
from datetime import datetime  
import pandas as pd  
import base64

# Configuración y almacenamiento de datos  
DB_FILE = "reservas.json"  
CLAVE_CANCELACION = "Inmaculada2026"   

AULAS_RECURSOS = [  
    "Notebooks", "Equipo de Sonido Grande", "Equipo de Sonido Chico",  
    "Laboratorio", "Salón de Usos Múltiples (SUM)",   
    "Proyector Móvil A", "Biblioteca", "Tablets"  
]  

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

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# Configuración de página  
st.set_page_config(page_title="Gestión de Espacios - IIC", page_icon="🏫", layout="centered")  

# Estilos CSS para forzar fondo claro, tipografía elegante y máxima legibilidad
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    /* Forzar fondo blanco y color de texto general oscuro en toda la app */
    .stApp {
        background-color: #f8fafc !important;
        color: #1e293b !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-bottom: 3px solid #E6C653;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        margin-bottom: 25px;
    }
    
    .header-logo {
        height: 85px;
        width: auto;
        image-rendering: -webkit-optimize-contrast;
        image-rendering: crisp-edges;
    }

    /* Ajustar contenedores y tarjetas a blanco nítido */
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }

    /* Textos y etiquetas legibles */
    label, .stTextInput label, .stSelectbox label, .stDateInput label {
        color: #1e293b !important;
        font-weight: 600 !important;
    }

    .stButton>button {
        font-weight: 600;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

reservas_actuales = cargar_reservas()  

# --- ENCABEZADO INSTITUCIONAL CON LOGO NÍTIDO ---
logo_b64 = get_base64_image("LOGO.png")

if logo_b64:
    header_html = f"""
    <div class="header-container">
        <img src="data:image/png;base64,{logo_b64}" class="header-logo" alt="Logo Instituto Inmaculada Concepción">
        <div>
            <h2 style="color: #0b1c3c; margin: 0; font-weight: 700; font-size: 1.6rem; letter-spacing: -0.5px;">INSTITUTO INMACULADA CONCEPCIÓN</h2>
            <p style="color: #64748b; font-weight: 600; font-size: 0.85rem; margin-top: 4px; letter-spacing: 0.5px; text-transform: uppercase;">Sistema Digital de Reserva de Espacios</p>
        </div>
    </div>
    """
else:
    header_html = """
    <div class="header-container" style="justify-content: center; text-align: center;">
        <div>
            <h2 style="color: #0b1c3c; margin: 0; font-weight: 700; font-size: 1.6rem;">INSTITUTO INMACULADA CONCEPCIÓN</h2>
            <p style="color: #64748b; font-weight: 600; font-size: 0.85rem; margin-top: 4px; text-transform: uppercase;">SISTEMA DIGITAL DE RESERVA DE ESPACIOS</p>
        </div>
    </div>
    """

st.markdown(header_html, unsafe_allow_html=True)

# --- NAVEGACIÓN POR PESTAÑAS ---  
tab_nueva, tab_planilla, tab_cancelar = st.tabs(["📝 Nueva Reserva", "📋 Planilla y Disponibilidad", "❌ Cancelar Reserva"])  

# ==========================================  
# PESTAÑA 1: NUEVA RESERVA  
# ==========================================  
with tab_nueva:  
    st.markdown("<h4 style='color: #0b1c3c; font-weight: 600; margin-bottom: 15px;'>Registrar Solicitud de Espacio</h4>", unsafe_allow_html=True)  
    
    with st.container():  
        nombre_profesor = st.text_input("Nombre y Apellido del Docente:")  
        
        col1, col2 = st.columns(2)  
        with col1:  
            fecha_seleccionada = st.date_input("Fecha:", min_value=datetime.today())  
            fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")  
        with col2:  
            recurso_seleccionado = st.selectbox("Aula o Recurso requerido:", AULAS_RECURSOS)  
        
        turno_seleccionado = st.selectbox("Bloque Horario Escolar:", TURNOS)  
        
        es_fin_de_semana = fecha_seleccionada.weekday() in [5, 6]  
        
        if es_fin_de_semana:  
            st.error("🔒 El establecimiento se encuentra cerrado los fines de semana. Seleccione días de Lunes a Viernes.")  
        else:  
            if st.button("Confirmar y Bloquear Horario", type="primary", use_container_width=True):  
                if not nombre_profesor.strip():  
                    st.toast("⚠️ Complete su nombre para continuar.", icon="👤")  
                else:  
                    conflicto = False  
                    for r in reservas_actuales:  
                        if (r["fecha"] == fecha_str and r["recurso"] == recurso_seleccionado and r["turno"] == turno_seleccionado):  
                            conflicto = True  
                            profesor_ocupante = r["profesor"]  
                            break  
                    
                    if conflicto:  
                        st.error(f"❌ **Conflicto de reserva:** El espacio ya fue asignado al/la Prof. {profesor_ocupante} para este día y horario.")  
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
                        st.success(f"✅ Guardado. **{recurso_seleccionado}** asignado con éxito.")  
                        st.balloons()  
                        st.rerun()  

# ==========================================  
# PESTAÑA 2: PLANILLA Y DISPONIBILIDAD  
# ==========================================  
with tab_planilla:  
    st.markdown("<h4 style='color: #0b1c3c; font-weight: 600; margin-bottom: 15px;'>Planilla de Ocupación General</h4>", unsafe_allow_html=True)  
    
    if not reservas_actuales:  
        st.info("No se registran turnos ocupados en el sistema actual.")  
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
        
        with st.expander("🔍 Herramientas de filtrado y búsqueda"):  
            busqueda = st.text_input("Filtrar por apellido del docente o aula específica:")  
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
            label="📥 Descargar Reporte Completo (CSV)",  
            data=csv,  
            file_name=f"reservas_inmaculada_{datetime.today().strftime('%Y%m%d')}.csv",  
            mime="text/csv",  
            use_container_width=True  
        )  

# ==========================================  
# PESTAÑA 3: CANCELAR RESERVA  
# ==========================================  
with tab_cancelar:  
    st.markdown("<h4 style='color: #0b1c3c; font-weight: 600; margin-bottom: 15px;'>Anulación de Turnos Asignados</h4>", unsafe_allow_html=True)  
    
    if not reservas_actuales:  
        st.info("No hay reservas registradas en el sistema para poder cancelar.")  
    else:  
        st.write("Seleccioná la reserva que deseas eliminar del sistema:")  
        
        opciones_cancelar = []  
        for i, r in enumerate(reservas_actuales):  
            texto_reserva = f"{r['fecha']} | {r['recurso']} | {r['turno']} (Prof. {r['profesor']})"  
            opciones_cancelar.append((i, texto_reserva))  
        
        reserva_a_eliminar_idx = st.selectbox(  
            "Seleccionar turno a dar de baja:",  
            options=[opt[0] for opt in opciones_cancelar],  
            format_func=lambda x: next(opt[1] for opt in opciones_cancelar if opt[0] == x)  
        )  
        
        with st.container():  
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

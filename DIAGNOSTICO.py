import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tempfile

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Diagnóstico de Madurez Empresarial", layout="wide")

# Título y Descripción
st.title("🛠️ Diagnóstico Integral de Madurez Empresarial")
st.markdown("""
Este tablero interactivo te permitirá evaluar el estado actual de tu organización.
Responde las siguientes secciones con honestidad para obtener tu **Nivel de Madurez** y tu **Hoja de Ruta**.
""")

# --- CLASE PARA GENERAR PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Diagnostico de Madurez Empresarial', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)

    st.header("👤 Datos de la Empresa")
    nombre_empresa = st.text_input("Nombre de la Empresa", "Empresa Ejemplo")
    nombre_contacto = st.text_input("Nombre del Contacto", "Juan Pérez")
    email_contacto = st.text_input("Correo del Cliente (Opcional)")

# Funciones de ayuda
def obtener_puntaje(opcion):
    return int(opcion.split(")")[0].replace("(", "").strip())

col1, col2 = st.columns([1, 1])

# Diccionarios de Opciones (Copiados de nuestro trabajo anterior)
opts_liderazgo = [
    "(1) Dependencia Total: El dueño toma el 100% de las decisiones.",
    "(2) Delegación Incipiente: Existen encargados sin autoridad real.",
    "(3) Estructura Funcional: Organigrama claro, gerentes resuelven el día a día.",
    "(4) Gestión por Indicadores: Decisiones basadas en KPIs y reportes.",
    "(5) Gobierno Corporativo: Consejo, sucesión y cultura de autogestión."

 opts_procesos = [
    "(1) Tribal/Empírico: Conocimiento solo en la cabeza de la gente.",
    "(2) Intentos Aislados: Documentos desactualizados ('Letra muerta').",
    "(3) Estandarización Básica: Procesos clave definidos y seguidos.",
    "(4) Gestión de Calidad: Todo documentado y auditado (ISO).",
    "(5) Mejora Continua: Optimización constante (Lean/Six Sigma)."
]   

opts_tecnologia = [
    "(1) Analógico: Cuadernos, notas físicas o memoria.",
    "(2) Ofimática Básica: Excel desconectados, errores manuales.",
    "(3) Sistemas Aislados: Software contable y ventas no se hablan.",
    "(4) Integración (ERP): Sistema centralizado, fuente única de verdad.",
    "(5) Inteligencia de Negocios: Dashboards, predicción e IA."
]

opts_financiera = [
    "(1) Caja Ciega: Gestión por flujo diario, sin visibilidad real.",
    "(2) Contabilidad Fiscal: Solo para impuestos, información tardía.",
    "(3) Reportes Básicos: Revisión periódica de P&L.",
    "(4) Gestión por KPIs: Monitoreo mensual de márgenes y EBITDA.",
    "(5) Finanzas Predictivas: Proyecciones y modelos de riesgo."
]

opts_mercado = [
    "(1) Invisible: Clientes compran por precio/cercanía.",
    "(2) Genérico: Oferta similar a la competencia.",
    "(3) Reconocido: Buena reputación en nicho específico.",
    "(4) Referente: Top of Mind, propuesta de valor clara.",
    "(5) Dominante/Innovador: Marcamos la tendencia del mercado."
]

with col1:
   st.subheader("A. Liderazgo")
    r_liderazgo = st.radio("Nivel actual:", opts_liderazgo)
    p_liderazgo = obtener_puntaje(r_liderazgo)

    st.subheader("B. Procesos")
    r_procesos = st.radio("Nivel actual:", opts_procesos)
    p_procesos = obtener_puntaje(r_procesos)

    st.subheader("C. Tecnología")
    r_tecnologia = st.radio("Nivel actual:", opts_tecnologia)
    p_tecnologia = obtener_puntaje(r_tecnologia)

with col2:
   st.subheader("D. Salud Financiera")
    r_financiera = st.radio("Nivel actual:", opts_financiera)
    p_financiera = obtener_puntaje(r_financiera)

    st.subheader("E. Mercado")
    r_mercado = st.radio("Nivel actual:", opts_mercado)
    p_mercado = obtener_puntaje(r_mercado)

# Cálculos
puntaje_total = p_liderazgo + p_procesos + p_tecnologia + p_financiera + p_mercado
puntaje_maximo = 25
porcentaje = (puntaje_total / puntaje_maximo) * 100

# Lógica de Segmentación (Backend)
if porcentaje < 40:
    nivel = "INICIAL 🔴"
    mensaje = "Alto Riesgo Operativo."
    dolor = "La empresa depende totalmente del dueño y procesos manuales."
    medicina = "💊 Receta: Programa de Estructura y Control Básico (3 Meses)."
    accion = "Necesitas documentar lo básico y delegar tareas operativas urgentemente."
elif porcentaje < 70:
    nivel = "EN DESARROLLO 🟡"
    mensaje = "Procesos Definidos pero no Optimizados."
    dolor = "Existen bases, pero están desconectadas. Hay 'islas' de información."
    medicina = "💉 Receta: Consultoría de Integración y Estandarización."
    accion = "El foco debe estar en conectar tus áreas y asegurar que los procesos se cumplan siempre."
else:
    nivel = "OPTIMIZADO 🟢"
    mensaje = "Enfoque en Innovación y Escalabilidad."
    dolor = "El reto ya no es el orden, sino el crecimiento acelerado."
    medicina = "🚀 Receta: Consejo Consultivo de Expansión & Transformación Digital."
    accion = "Es momento de usar tus datos para predecir el futuro y automatizar con IA."
    
# Visualización
st.divider()
st.header("📊 Resultados del Diagnóstico")

# Métricas Principales
m1, m2, m3 = st.columns(3)
m1.metric("Puntaje Total", f"{puntaje_total}/25")
m2.metric("Índice de Madurez", f"{porcentaje:.0f}%")
m3.metric("Nivel Detectado", nivel)

# Gráficas
tab1, tab2 = st.tabs(["🕸️ Radar de Balance", "📊 Detalle por Área"])

# Datos para gráficas
datos = {
    'Área': ['Liderazgo', 'Procesos', 'Tecnología', 'Finanzas', 'Mercado'],
    'Puntaje': [p_liderazgo, p_procesos, p_tecnologia, p_financiera, p_mercado]
}
df = pd.DataFrame(datos)

with tab1:
    # Gráfico de Radar (Spider Plot) - Muy usado en consultoría
    fig = go.Figure(data=go.Scatterpolar(
        r=df['Puntaje'],
        theta=df['Área'],
        fill='toself',
        name=nombre_empresa if nombre_empresa else "Empresa"
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False,
        title="Balance de Madurez (¿Dónde está la llanta ponchada?)"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.bar_chart(df.set_index('Área'))

# --- LA MEDICINA (Recomendación) ---
st.success(f"### Diagnóstico Final: {nivel}")
st.markdown(f"**Detectamos:** {mensaje}")
st.markdown(f"**Tu Dolor Principal:** {dolor}")
st.divider()
st.markdown(f"## {medicina}")
st.info(f"**Siguiente Paso Recomendado:** {accion}")
# --- BOTÓN DE ENVÍO ---
if st.button("Generar Reporte y Enviar al Consultor"):
    if not nombre_empresa:
        st.warning("Por favor escribe el nombre de la empresa.")
    else:
        # 1. Crear PDF
        pdf_bytes = generar_pdf(nombre_empresa, nombre_contacto, nivel, puntaje_total, medicina)
        
        # 2. Enviar Correo (A ti mismo)
        tu_correo = st.secrets["correo"]["usuario"] # Se enviará a tu propio correo
        exito = enviar_correo(tu_correo, f"Nuevo Lead: {nombre_empresa}", 
                              f"Resultados del diagnóstico adjuntos.\nCliente: {nombre_contacto}", 
                              pdf_bytes, "diagnostico.pdf")
        
        if exito:
            st.success("¡Reporte enviado exitosamente! Nos pondremos en contacto pronto.")
            # Opción de descarga para el cliente
            st.download_button(label="Descargar mi copia en PDF", 
                               data=pdf_bytes, 
                               file_name="mi_diagnostico.pdf", 
                               mime="application/pdf")


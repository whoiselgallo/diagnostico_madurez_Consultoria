import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Diagnóstico de Madurez Empresarial", layout="wide")

# Título y Descripción
st.title("🛠️ Diagnóstico Integral de Madurez Empresarial")
st.markdown("""
Este tablero interactivo te permitirá evaluar el estado actual de tu organización.
Responde las siguientes secciones con honestidad para obtener tu **Nivel de Madurez** y tu **Hoja de Ruta**.
""")

# --- BARRA LATERAL (DATOS) ---
with st.sidebar:
    st.header("👤 Datos de la Empresa")
    nombre_empresa = st.text_input("Nombre de la Empresa", "Empresa Ejemplo")
    nombre_contacto = st.text_input("Nombre del Contacto", "Juan Pérez")
    email_contacto = st.text_input("Correo del Cliente (Opcional)")

# --- CLASE Y FUNCIONES PARA PDF Y CORREO ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Diagnostico de Madurez Empresarial', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generar_pdf(nombre_empresa, contacto, nivel, puntaje, medicina):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Función para limpiar texto (quita emojis y caracteres raros)
    def clean(text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    # Contenido del PDF (Usamos clean() para evitar errores)
    pdf.cell(200, 10, txt=clean(f"Empresa: {nombre_empresa}"), ln=True)
    pdf.cell(200, 10, txt=clean(f"Contacto: {contacto}"), ln=True)
    pdf.cell(200, 10, txt=clean(f"Nivel Detectado: {nivel}"), ln=True)
    pdf.cell(200, 10, txt=clean(f"Puntaje: {puntaje}/25"), ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Recomendacion Estrategica:", ln=True)
    pdf.set_font("Arial", size=11)
    
    # Multi_cell para textos largos
    pdf.multi_cell(0, 10, txt=clean(medicina))
    
    return pdf.output(dest='S').encode('latin-1')

def enviar_correo(destinatario, asunto, cuerpo, archivo_pdf, nombre_archivo):
    try:
        remitente = st.secrets["correo"]["usuario"]
        password = st.secrets["correo"]["password"]
    except:
        st.error("No se encontraron las credenciales de correo en Secrets.")
        return False
    
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain'))
    
    # Adjuntar PDF
    part = MIMEBase('application', "octet-stream")
    part.set_payload(archivo_pdf)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{nombre_archivo}"')
    msg.attach(part)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error al enviar correo: {e}")
        return False

# Funciones de ayuda
def obtener_puntaje(opcion):
    return int(opcion.split(")")[0].replace("(", "").strip())

# --- INTERFAZ DEL CUESTIONARIO ---
col1, col2 = st.columns([1, 1])

# Opciones
opts_liderazgo = [
    "(1) Dependencia Total: El dueño toma el 100% de las decisiones.",
    "(2) Delegación Incipiente: Existen encargados sin autoridad real.",
    "(3) Estructura Funcional: Organigrama claro, gerentes resuelven el día a día.",
    "(4) Gestión por Indicadores: Decisiones basadas en KPIs y reportes.",
    "(5) Gobierno Corporativo: Consejo, sucesión y cultura de autogestión."
]
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

# --- CÁLCULOS ---
puntaje_total = p_liderazgo + p_procesos + p_tecnologia + p_financiera + p_mercado
puntaje_maximo = 25
porcentaje = (puntaje_total / puntaje_maximo) * 100

# Lógica de Segmentación (CREAMOS VARIABLES SEPARADAS PARA PDF Y WEB)
if porcentaje < 40:
    # Variables con Emojis para la Web
    nivel_web = "INICIAL 🔴"
    mensaje = "Alto Riesgo Operativo."
    dolor = "La empresa depende totalmente del dueño y procesos manuales."
    medicina_web = "💊 Receta: Programa de Estructura y Control Básico (3 Meses)."
    
    # Variables LIMPIAS para el PDF
    nivel_pdf = "INICIAL"
    medicina_pdf = "Receta: Programa de Estructura y Control Basico (3 Meses).\nNecesitas documentar lo basico y delegar tareas operativas urgentemente."
    accion = "Necesitas documentar lo básico y delegar tareas operativas urgentemente."

elif porcentaje < 70:
    nivel_web = "EN DESARROLLO 🟡"
    mensaje = "Procesos Definidos pero no Optimizados."
    dolor = "Existen bases, pero están desconectadas. Hay 'islas' de información."
    medicina_web = "💉 Receta: Consultoría de Integración y Estandarización."
    
    nivel_pdf = "EN DESARROLLO"
    medicina_pdf = "Receta: Consultoria de Integracion y Estandarizacion.\nEl foco debe estar en conectar tus areas y asegurar que los procesos se cumplan."
    accion = "El foco debe estar en conectar tus áreas y asegurar que los procesos se cumplan siempre."

else:
    nivel_web = "OPTIMIZADO 🟢"
    mensaje = "Enfoque en Innovación y Escalabilidad."
    dolor = "El reto ya no es el orden, sino el crecimiento acelerado."
    medicina_web = "🚀 Receta: Consejo Consultivo de Expansión & Transformación Digital."
    
    nivel_pdf = "OPTIMIZADO"
    medicina_pdf = "Receta: Consejo Consultivo de Expansion & Transformacion Digital.\nEs momento de usar tus datos para predecir el futuro y automatizar con IA."
    accion = "Es momento de usar tus datos para predecir el futuro y automatizar con IA."

# --- RESULTADOS VISUALES (USAMOS VARIABLES WEB) ---
st.divider()
st.header("📊 Resultados del Diagnóstico")

m1, m2, m3 = st.columns(3)
m1.metric("Puntaje Total", f"{puntaje_total}/25")
m2.metric("Índice de Madurez", f"{porcentaje:.0f}%")
m3.metric("Nivel Detectado", nivel_web)

tab1, tab2 = st.tabs(["🕸️ Radar de Balance", "📊 Detalle por Área"])

datos = {
    'Área': ['Liderazgo', 'Procesos', 'Tecnología', 'Finanzas', 'Mercado'],
    'Puntaje': [p_liderazgo, p_procesos, p_tecnologia, p_financiera, p_mercado]
}
df = pd.DataFrame(datos)

with tab1:
    fig = go.Figure(data=go.Scatterpolar(
        r=df['Puntaje'],
        theta=df['Área'],
        fill='toself',
        name=nombre_empresa if nombre_empresa else "Empresa"
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False,
        title="Balance de Madurez"
    )
    # Fix para el warning de container_width
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.bar_chart(df.set_index('Área'))

st.success(f"### Diagnóstico Final: {nivel_web}")
st.markdown(f"**Detectamos:** {mensaje}")
st.markdown(f"**Tu Dolor Principal:** {dolor}")
st.divider()
st.markdown(f"## {medicina_web}")
st.info(f"**Siguiente Paso Recomendado:** {accion}")

# --- BOTÓN DE ENVÍO (USAMOS VARIABLES PDF) ---
if st.button("Generar Reporte y Enviar al Consultor"):
    if not nombre_empresa:
        st.warning("Por favor escribe el nombre de la empresa.")
    else:
        # 1. Crear PDF con variables LIMPIAS
        pdf_bytes = generar_pdf(nombre_empresa, nombre_contacto, nivel_pdf, puntaje_total, medicina_pdf)
        
        # 2. Enviar Correo
        try:
            tu_correo = st.secrets["correo"]["usuario"] 
            exito = enviar_correo(tu_correo, f"Nuevo Lead: {nombre_empresa}", 
                                  f"Resultados del diagnóstico adjuntos.\nCliente: {nombre_contacto}", 
                                  pdf_bytes, "diagnostico.pdf")
            
            if exito:
                st.success("¡Reporte enviado exitosamente! Nos pondremos en contacto pronto.")
                st.download_button(label="Descargar mi copia en PDF", 
                                   data=pdf_bytes, 
                                   file_name="mi_diagnostico.pdf", 
                                   mime="application/pdf")
        except Exception as e:
            st.error(f"Error de configuración de secretos: {e}")

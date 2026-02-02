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

# --- CLASE PARA GENERAR PDF ---
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
    
    # Contenido
    pdf.cell(200, 10, txt=f"Empresa: {nombre_empresa}", ln=True)
    pdf.cell(200, 10, txt=f"Contacto: {contacto}", ln=True)
    pdf.cell(200, 10, txt=f"Nivel Detectado: {nivel}", ln=True)
    pdf.cell(200, 10, txt=f"Puntaje: {puntaje}/25", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Recomendacion Estrategica:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, txt=medicina)
    
    return pdf.output(dest='S').encode('latin-1')

# --- FUNCIÓN DE ENVÍO DE CORREO ---
def enviar_correo(destinatario, asunto, cuerpo, archivo_pdf, nombre_archivo):
    # Credenciales desde Streamlit Secrets (Seguridad)
    remitente = st.secrets["correo"]["usuario"]
    password = st.secrets["correo"]["password"]
    
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
    
    # Enviar
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

# --- INTERFAZ PRINCIPAL ---
st.title("🛠️ Diagnóstico Integral de Madurez Empresarial")

# Barra Lateral
with st.sidebar:
    st.header("👤 Datos de la Empresa")
    nombre_empresa = st.text_input("Nombre de la Empresa", "Empresa Ejemplo")
    nombre_contacto = st.text_input("Nombre del Contacto", "Juan Pérez")
    email_contacto = st.text_input("Correo del Cliente (Opcional)")

# Funciones de ayuda
def obtener_puntaje(opcion):
    return int(opcion.split(")")[0].replace("(", "").strip())

col1, col2 = st.columns([1, 1])

opts_liderazgo = ["(1) Dependencia Total", "(2) Delegación Incipiente", "(3) Estructura Funcional", "(4) Gestión por Indicadores", "(5) Gobierno Corporativo"]
opts_procesos = ["(1) Tribal/Empírico", "(2) Intentos Aislados", "(3) Estandarización Básica", "(4) Gestión de Calidad", "(5) Mejora Continua"]
opts_tecnologia = ["(1) Analógico", "(2) Ofimática Básica", "(3) Sistemas Aislados", "(4) Integración (ERP)", "(5) Inteligencia de Negocios"]
opts_financiera = ["(1) Caja Ciega", "(2) Contabilidad Fiscal", "(3) Reportes Básicos", "(4) Gestión por KPIs", "(5) Finanzas Predictivas"]
opts_mercado = ["(1) Invisible", "(2) Genérico", "(3) Reconocido", "(4) Referente", "(5) Dominante/Innovador"]

with col1:
    p_liderazgo = obtener_puntaje(st.radio("A. Liderazgo", opts_liderazgo))
    p_procesos = obtener_puntaje(st.radio("B. Procesos", opts_procesos))
    p_tecnologia = obtener_puntaje(st.radio("C. Tecnología", opts_tecnologia))

with col2:
    p_financiera = obtener_puntaje(st.radio("D. Salud Financiera", opts_financiera))
    p_mercado = obtener_puntaje(st.radio("E. Mercado", opts_mercado))

# Cálculos
puntaje_total = p_liderazgo + p_procesos + p_tecnologia + p_financiera + p_mercado
porcentaje = (puntaje_total / 25) * 100

if porcentaje < 40:
    nivel = "INICIAL"
    medicina = "RECETA: Programa de Estructura y Control Básico. Necesitas documentar lo básico y delegar."
elif porcentaje < 70:
    nivel = "EN DESARROLLO"
    medicina = "RECETA: Consultoría de Integración. El foco debe estar en conectar tus áreas."
else:
    nivel = "OPTIMIZADO"
    medicina = "RECETA: Consejo Consultivo de Expansión. Es momento de automatizar con IA."

# Visualización
st.divider()
st.metric("Puntaje Total", f"{puntaje_total}/25", f"{nivel}")

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

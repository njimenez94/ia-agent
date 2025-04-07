import streamlit as st
import pandas as pd # Añadir Pandas
import os # Para manejo de paths

# Importar funciones de los otros módulos
from summarizer import summarize_website # Asume que está en la carpeta app
from data_analyzer import read_uploaded_file, analyze_dataframe_with_llm # El nuevo módulo

# --- Configuración de Página ---
st.set_page_config(
    page_title="Asistente IA: Resúmenes y Análisis",
    page_icon="✨",
    layout="wide"
)

# --- Cargar CSS Personalizado ---
# Construir path relativo al script actual para asegurar que funcione
# independientemente de dónde se ejecute streamlit
current_dir = os.path.dirname(os.path.abspath(__file__))
css_file_path = os.path.join(current_dir, '..', 'static', 'style.css') # Va un nivel arriba a static
try:
    with open(css_file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("No se pudo encontrar el archivo CSS en 'static/style.css'")


# --- Título Principal ---
st.title("Asistente IA para Resúmenes y Análisis de Datos")
st.markdown("Utiliza modelos de IA Open Source (vía Ollama) para resumir sitios web o analizar archivos de datos.")

# --- Selección de Modelo Global (Opcional, o por pestaña) ---
# Podrías tener un selector general, o uno específico en cada pestaña
# Por simplicidad, usaremos uno específico por pestaña ahora.
available_models = ["llama3.2", "llama3.1", "mistral", "phi3"] # Ajusta a tus modelos Ollama disponibles


# --- Pestañas para Funcionalidades ---
tab1, tab2 = st.tabs(["📝 Resumir Sitio Web", "📊 Analizar Archivo de Datos"])

# --- Pestaña 1: Resumir Sitio Web ---
with tab1:
    st.header("Resumidor de Sitios Web")
    st.markdown("""
    Ingresa la URL de un sitio web para obtener un resumen generado por IA.
    """)

    # Selección de modelo para resumen web
    model_web = st.selectbox(
        "Seleccionar modelo para Resumen Web",
        available_models,
        index=0, # Modelo por defecto
        key="web_model_select"
        )

    url = st.text_input(
        "Ingresa la URL del sitio web",
        placeholder="https://ejemplo.com",
        key="url_input"
        )

    if st.button("Generar Resumen Web", type="primary", key="summarize_web_button"):
        if url:
            # Validar URL simple
            if not (url.startswith('http://') or url.startswith('https://')):
                 st.warning("Por favor, ingresa una URL válida (que empiece con http:// o https://)")
            else:
                with st.spinner(f"Analizando sitio web con {model_web}..."):
                    # Llamar a la función de resumen
                    result = summarize_website(url, model=model_web)

                    if result["success"]:
                        st.success("¡Resumen generado con éxito!")
                        if result.get("website_title"):
                            st.subheader(f"Sitio: {result['website_title']}")
                        st.markdown("## Resumen")
                        # Usar un contenedor para el markdown con estilo
                        with st.container(border=True):
                             st.markdown(result["summary"])

                        # Añadir botón de descarga
                        try:
                            file_name_md = f"resumen_{result.get('website_title','sitio_web').replace(' ','_')}.md"
                            st.download_button(
                                label="Descargar resumen como Markdown",
                                data=result["summary"],
                                file_name=file_name_md,
                                mime="text/markdown"
                            )
                        except Exception as e:
                             st.error(f"No se pudo generar botón de descarga: {e}")

                    else:
                        st.error(f"Error al generar resumen: {result['error']}")
        else:
            st.warning("Por favor, ingresa una URL.")

# --- Pestaña 2: Analizar Archivo de Datos ---
with tab2:
    st.header("Analizador de Archivos de Datos")
    st.markdown("""
    Sube un archivo CSV o Excel para obtener un análisis y resumen generado por IA.
    **Importante:** La calidad del análisis depende de la estructura del archivo y los nombres de las columnas.
    """)

    # Selección de modelo para análisis de datos
    model_data = st.selectbox(
        "Seleccionar modelo para Análisis de Datos",
        available_models,
        index=0, # Modelo por defecto
        key="data_model_select"
        )

    uploaded_file = st.file_uploader(
        "Carga tu archivo (CSV o Excel)",
        type=['csv', 'xlsx', 'xls'], # Añadir .xls por si acaso
        key="data_file_uploader"
        )

    if st.button("Analizar Datos del Archivo", type="primary", key="analyze_data_button"):
        if uploaded_file is not None:
            with st.spinner("Leyendo y procesando archivo..."):
                df, error_read = read_uploaded_file(uploaded_file) # Usar la función del módulo

            if error_read:
                st.error(f"Error al leer el archivo: {error_read}")
            elif df is not None:
                st.success("Archivo leído con éxito.")
                st.dataframe(df.head()) # Mostrar preview

                with st.spinner(f"Analizando datos con {model_data}..."):
                    # Llamar a la función de análisis del DataFrame
                    result = analyze_dataframe_with_llm(df, model_name=model_data)

                    if result["success"]:
                        st.success("¡Análisis generado con éxito!")
                        st.markdown("## Resumen del Análisis")
                        # Usar un contenedor para el markdown con estilo
                        with st.container(border=True):
                             st.markdown(result["summary"])

                        # Añadir botón de descarga para el análisis
                        try:
                            file_name_analysis = f"analisis_{uploaded_file.name}.md"
                            st.download_button(
                                label="Descargar análisis como Markdown",
                                data=result["summary"],
                                file_name=file_name_analysis,
                                mime="text/markdown"
                            )
                        except Exception as e:
                             st.error(f"No se pudo generar botón de descarga del análisis: {e}")

                    else:
                        st.error(f"Error durante el análisis con IA: {result['error']}")
            else:
                 st.error("No se pudo obtener un DataFrame del archivo.") # Error genérico si read_uploaded_file falla inesperadamente
        else:
            st.warning("Por favor, carga un archivo primero.")


# --- Footer (Común a ambas pestañas) ---
st.markdown("---")
# Usar st.markdown o st.html para el footer si necesitas más control
st.markdown(
    """
    <div style="text-align: center; padding: 10px; margin-top: 30px;">
        <p style="font-size: 14px; color: #555;">
            Desarrollado por <b>Nicolás Jiménez</b> |
            <a href="https://github.com/njimenez94" target="_blank" style="text-decoration: none; color: #0D47A1;">GitHub</a> |
            <a href="https://www.linkedin.com/in/nicolas-jd/" target="_blank" style="text-decoration: none; color: #0D47A1;">LinkedIn</a>
        </p>
        <p style="font-size: 12px; color: #777;">
            Construido con ❤️ usando Streamlit, Pandas & Ollama Open Source Models.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
# st.caption("Desarrollado con ❤️ usando Streamlit, Pandas & Ollama Open Source Models.") # Alternativa más simple
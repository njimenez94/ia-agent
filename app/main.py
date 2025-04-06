import streamlit as st
from summarizer import summarize_website

# Set page configuration
st.set_page_config(
    page_title="Resumen de Sitios Web",
    page_icon="📝",
    layout="wide"
)

# Add custom CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# App title and description
st.title("Resumidor de sitios web usando modelos Open Source")
st.markdown("""
Esta aplicación te permite obtener un resumen de cualquier sitio web utilizando 
modelos de lenguaje generativo a través de Ollama.
""")

# Model selection
models = ["llama3.2", "llama3.1", "mistral", "phi3"]
selected_model = st.selectbox("Seleccionar modelo", models)

# URL input
url = st.text_input("Ingresa la URL del sitio web que deseas resumir", 
                   placeholder="https://ejemplo.com")

# Process button
if st.button("Generar resumen", type="primary"):
    if url:
        with st.spinner("Analizando sitio web..."):
            # Call the summarization function
            result = summarize_website(url, model=selected_model)
            
            if result["success"]:
                st.success("¡Resumen generado con éxito!")
                
                # Show website title if available
                if "website_title" in result:
                    st.subheader(f"Sitio: {result['website_title']}")
                
                # Display the summary
                st.markdown("## Resumen")
                st.markdown(result["summary"])
                
                # Add option to download as markdown
                st.download_button(
                    label="Descargar resumen como Markdown",
                    data=result["summary"],
                    file_name="resumen.md",
                    mime="text/markdown"
                )
            else:
                st.error(f"Error: {result['error']}")
    else:
        st.warning("Por favor, ingresa una URL válida")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 10px; margin-top: 30px;">
        <p style="font-size: 16px;">
            Desarrollado por <b>Nicolás Jiménez</b> | 
            <a href="https://github.com/njimenez94" target="_blank">
                <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20" style="vertical-align: middle; margin-right: 3px;">
            GitHub
            </a>
            | 
            <a href="https://www.linkedin.com/in/nicolas-jd/" target="_blank">
                <img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width="20" style="vertical-align: middle; margin-right: 3px;">
            LinkedIn
            </a>
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)
st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y Ollama")
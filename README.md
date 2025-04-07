1.  **`environment.yml`**:
    * **Propósito**: Este archivo define el entorno de Conda necesario para ejecutar tu proyecto. Lista todas las bibliotecas de Python (dependencias) que tu aplicación necesita, junto con sus versiones específicas.
    * **Funcionamiento**: Alguien que quiera ejecutar tu código puede usar este archivo con Conda para crear un entorno idéntico, asegurando que el código funcione correctamente sin problemas de compatibilidad de bibliotecas.
    * **Dependencias Clave**:
        * `streamlit`: Para crear la interfaz web interactiva.
        * `requests`: Para descargar el contenido HTML de la URL proporcionada.
        * `beautifulsoup4`: Para analizar (parsear) el HTML y extraer el texto relevante.
        * `ollama`: La biblioteca cliente para interactuar con los modelos de lenguaje que se ejecutan localmente a través de Ollama.
        * `python=3.10`: Especifica la versión de Python requerida.
        * Otras como `pandas`, `numpy`, etc., que aunque pueden no ser usadas directamente en el flujo principal de resumen, son dependencias de otras bibliotecas (como Streamlit o PyArrow).

2.  **`static/style.css`**:
    * **Propósito**: Contiene reglas de CSS personalizadas para darle estilo a la apariencia de tu aplicación Streamlit.
    * **Funcionamiento**: El archivo `main.py` lee este CSS y lo inyecta en la página web, sobrescribiendo o complementando los estilos por defecto de Streamlit. Define colores, tamaños de fuente, márgenes, padding, bordes, etc., para elementos como títulos, botones, campos de texto, mensajes de éxito/error y el contenedor del resumen.

3.  **`app/website.py`**:
    * **Propósito**: Este módulo se encarga de obtener y procesar el contenido del sitio web.
    * **Clase `Website`**:
        * `__init__(self, url, headers=None)`:
            * Recibe la URL del sitio web.
            * Usa la biblioteca `requests` para descargar el contenido HTML de la URL. Incluye cabeceras (`User-Agent`) para simular una solicitud de navegador y evitar bloqueos simples.
            * Maneja errores de HTTP (ej. 404 Not Found, 500 Internal Server Error).
            * Utiliza `BeautifulSoup` para parsear el HTML descargado.
            * Intenta extraer el título de la página (`<title>`).
            * **Limpieza Clave**: Elimina etiquetas HTML que generalmente no contienen contenido principal relevante para un resumen (como `<script>`, `<style>`, `<nav>`, `<footer>`, `<img>`, `<input>`) usando `decompose()`.
            * Extrae el texto principal del `<body>` usando `get_text()`, uniendo líneas con saltos de línea (`\n`) y eliminando espacios extra (`strip=True`).
            * Maneja excepciones generales durante la obtención o el parseo, guardando el estado (`status`) y el mensaje de error (`error`).
        * `is_valid()`: Un método simple para verificar si la obtención y el parseo del sitio web fueron exitosos.
    * **Función `create_user_prompt(website)`**:
        * Toma un objeto `Website` ya procesado.
        * Construye el *prompt* (la instrucción) que se le dará al modelo de lenguaje. Este prompt incluye el título del sitio y el texto extraído, pidiendo específicamente un resumen en formato markdown y en español.

4.  **`app/summarizer.py`**:
    * **Propósito**: Orquesta el proceso de resumen interactuando con el modelo de Ollama.
    * **Función `get_system_prompt()`**:
        * Define el *prompt del sistema*. Esta es una instrucción general que le dice al modelo cuál es su rol o cómo debe comportarse. Aquí, le indica que es un asistente que resume sitios web, debe ignorar texto de navegación y responder en markdown español.
    * **Función `create_messages(website)`**:
        * Prepara la estructura de mensajes requerida por la API de chat de Ollama. Generalmente es una lista de diccionarios, alternando roles ("system", "user"). Combina el prompt del sistema con el prompt del usuario (generado en `website.py`).
    * **Función `summarize_website(url, model="llama3.2")`**:
        * Es la función principal de este módulo, llamada desde la interfaz de Streamlit.
        * Crea una instancia de la clase `Website` para obtener y limpiar el contenido de la URL.
        * Verifica si la carga del sitio fue válida (`website.is_valid()`). Si no, retorna un diccionario indicando el fallo y el error.
        * Prepara los mensajes para Ollama usando `create_messages()`.
        * Llama a `ollama.chat()`, pasándole el nombre del modelo seleccionado (`model`) y los mensajes preparados.
        * Extrae el contenido de la respuesta del modelo (el resumen).
        * Retorna un diccionario indicando éxito (`success: True`), el resumen (`summary`), el título del sitio (`website_title`) y `error: None`.
        * Incluye un manejo de excepciones general por si falla la llamada a Ollama.

5.  **`app/main.py`**:
    * **Propósito**: Es el punto de entrada de la aplicación. Define la interfaz de usuario usando Streamlit y maneja la interacción con el usuario.
    * **Configuración Inicial**:
        * `st.set_page_config()`: Configura el título de la pestaña del navegador, el ícono y el layout de la página.
        * Carga y aplica el CSS personalizado desde `static/style.css`.
    * **Interfaz de Usuario (UI)**:
        * `st.title()`, `st.markdown()`: Muestra el título principal y una descripción de la aplicación.
        * `st.selectbox()`: Crea un menú desplegable para que el usuario elija qué modelo de Ollama usar (de una lista predefinida).
        * `st.text_input()`: Un campo de texto para que el usuario ingrese la URL del sitio web a resumir.
        * `st.button()`: Un botón que el usuario presiona para iniciar el proceso de resumen.
    * **Lógica Principal**:
        * Cuando el botón "Generar resumen" es presionado:
            * Verifica si se ingresó una URL. Si no, muestra una advertencia (`st.warning`).
            * Si hay URL, muestra un indicador de carga (`st.spinner`).
            * Llama a la función `summarize_website()` del módulo `summarizer`, pasándole la URL y el modelo seleccionado.
            * Revisa el resultado devuelto por `summarize_website()`:
                * Si `success` es `True`: Muestra un mensaje de éxito (`st.success`), el título del sitio (si se obtuvo), el resumen generado usando `st.markdown()` (para interpretar el formato markdown), y un botón (`st.download_button`) para descargar el resumen como archivo `.md`.
                * Si `success` es `False`: Muestra un mensaje de error (`st.error`) con el detalle del problema.
    * **Footer**: Añade un pie de página con información del desarrollador (Nicolás Jiménez) y enlaces a GitHub/LinkedIn, además de un mensaje sobre las tecnologías usadas.

**En Resumen:**

Tu proyecto es una aplicación web que:
1.  Presenta una interfaz simple (creada con Streamlit) donde el usuario puede pegar una URL y elegir un modelo de IA (Ollama).
2.  Al presionar el botón, descarga el contenido de la URL (`requests`).
3.  Limpia el HTML para extraer el texto principal (`BeautifulSoup`).
4.  Envía este texto, junto con instrucciones (prompts), al modelo de IA seleccionado que se ejecuta vía Ollama.
5.  Recibe el resumen generado por la IA.
6.  Muestra el resumen al usuario en la interfaz y ofrece una opción para descargarlo.
7.  Maneja errores en el proceso (URL inválida, fallo al descargar, error de la IA).
8.  Usa un archivo `environment.yml` para definir dependencias y un `style.css` para personalizar la apariencia.

Es un proyecto bien estructurado que separa las responsabilidades: la interfaz (`main.py`), el manejo del sitio web (`website.py`) y la interacción con la IA (`summarizer.py`).
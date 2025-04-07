import pandas as pd
import ollama
import io # Para leer el buffer del archivo subido

def create_data_analysis_prompt(df: pd.DataFrame):
    """
    Genera el prompt para el LLM basado en el DataFrame.
    Intenta realizar algunos cálculos básicos y presenta una muestra de datos.

    Args:
        df (pd.DataFrame): El DataFrame a analizar.

    Returns:
        str: El prompt para el LLM.
    """
    prompt_text = "### Análisis Solicitado: Datos Comerciales\n\n"
    prompt_text += f"Se ha cargado un archivo con {len(df)} filas/registros y {df.shape[1]} columnas.\n"
    prompt_text += f"Nombres de las columnas: {', '.join(df.columns)}\n\n"

    prompt_text += "### Resumen Estadístico y Cálculos Preliminares:\n"
    # Intenta generar un resumen estadístico básico para columnas numéricas
    try:
        numeric_cols = df.select_dtypes(include='number').columns
        if not numeric_cols.empty:
            prompt_text += "Estadísticas descriptivas (columnas numéricas):\n"
            prompt_text += df[numeric_cols].describe().to_markdown() + "\n\n"
        else:
            prompt_text += "No se encontraron columnas numéricas para estadísticas descriptivas.\n\n"
    except Exception as e:
        prompt_text += f"(No se pudo generar .describe(): {e})\n\n"

    # --- Intenta realizar cálculos específicos (¡AJUSTA ESTOS NOMBRES!) ---
    # Adapta los nombres 'Ventas', 'Producto', 'Departamento', 'Fecha' a los nombres REALES de tus columnas
    calculated_insights = []
    try:
        if 'Ventas' in df.columns:
            total_sales = df['Ventas'].sum()
            calculated_insights.append(f"- Ventas Totales Registradas: ${total_sales:,.2f}")
            if 'Producto' in df.columns:
                product_sales = df.groupby('Producto')['Ventas'].sum()
                if not product_sales.empty:
                    top_product = product_sales.idxmax()
                    top_product_sales = product_sales.max()
                    calculated_insights.append(f"- Producto con Mayores Ventas: {top_product} (${top_product_sales:,.2f})")
                    worst_product = product_sales.idxmin()
                    worst_product_sales = product_sales.min()
                    calculated_insights.append(f"- Producto con Menores Ventas: {worst_product} (${worst_product_sales:,.2f})")

            if 'Departamento' in df.columns:
                 dept_sales = df.groupby('Departamento')['Ventas'].sum()
                 if not dept_sales.empty:
                    top_dept = dept_sales.idxmax()
                    calculated_insights.append(f"- Departamento con Mayores Ventas: {top_dept}")
                    worst_dept = dept_sales.idxmin()
                    calculated_insights.append(f"- Departamento con Menores Ventas: {worst_dept}")

        # Puedes añadir más análisis aquí (ej. tendencias si hay fechas)

        if calculated_insights:
            prompt_text += "Insights Calculados Directamente:\n" + "\n".join(calculated_insights) + "\n\n"
        else:
            prompt_text += "No se pudieron calcular insights específicos (verifica nombres de columnas como 'Ventas', 'Producto', 'Departamento').\n\n"

    except KeyError as e:
        prompt_text += f"(Falta la columna '{e}' para cálculos específicos)\n\n"
    except Exception as e:
        prompt_text += f"(Error durante cálculos específicos: {e})\n\n"
    # --- Fin Cálculos Específicos ---

    prompt_text += "### Muestra de Datos (Primeras 5 Filas):\n"
    try:
        # Usar to_markdown para mejor formato si es posible
        prompt_text += df.head().to_markdown(index=False) + "\n\n"
    except Exception: # Fallback a to_string
         prompt_text += df.head().to_string() + "\n\n"


    # Limit prompt size (optional but recommended for large datasets/many columns)
    max_prompt_chars = 15000 # Ajusta según necesidad y modelo
    if len(prompt_text) > max_prompt_chars:
         prompt_text = prompt_text[:max_prompt_chars] + "\n... (prompt truncado)\n\n"


    prompt_text += "### INSTRUCCIÓN PARA EL MODELO:\n"
    prompt_text += "Actúa como un analista de negocios experto. Basándote ESTRICTAMENTE en la información y los datos proporcionados arriba, genera un resumen ejecutivo conciso en español para la gerencia. Destaca las tendencias clave, los puntos fuertes (ej. mejores productos/departamentos), los puntos débiles (ej. peores productos/departamentos) y cualquier otro insight relevante que puedas inferir DIRECTAMENTE de los datos mostrados. No inventes información que no esté presente. Usa un lenguaje claro y profesional, preferiblemente en formato de puntos clave (bullet points)."

    return prompt_text

def get_data_analysis_system_prompt():
    """
    Define el rol del sistema para el análisis de datos.
    """
    return "Eres un asistente de IA especializado en análisis de datos comerciales. Tu tarea es interpretar los datos y cálculos proporcionados y generar un resumen ejecutivo claro y conciso en español, enfocado en insights accionables para la gerencia. Responde únicamente basándote en la información dada."


def analyze_dataframe_with_llm(df: pd.DataFrame, model_name: str):
    """
    Analiza un DataFrame usando Ollama.

    Args:
        df (pd.DataFrame): El DataFrame a analizar.
        model_name (str): El nombre del modelo Ollama a usar.

    Returns:
        dict: Diccionario con el resultado del análisis.
    """
    if df is None or df.empty:
         return {"success": False, "summary": None, "error": "El DataFrame está vacío o no es válido."}

    try:
        # 1. Crear el prompt basado en el DataFrame
        user_prompt = create_data_analysis_prompt(df)

        # 2. Definir los mensajes para Ollama
        messages = [
            {"role": "system", "content": get_data_analysis_system_prompt()},
            {"role": "user", "content": user_prompt}
        ]

        # 3. Llamar a Ollama
        response = ollama.chat(model=model_name, messages=messages)

        # 4. Procesar la respuesta
        if response and "message" in response and "content" in response["message"]:
            summary = response["message"]["content"]
            # Simple post-processing: remove potential preamble if model adds it
            summary_lines = summary.split('\n')
            if "Aquí tienes un resumen ejecutivo" in summary_lines[0]:
                 summary = "\n".join(summary_lines[1:]).strip()

            return {"success": True, "summary": summary, "error": None}
        else:
            return {"success": False, "summary": None, "error": "La respuesta del modelo de IA no tuvo el formato esperado."}

    except ollama.ResponseError as e:
         # Specific Ollama error handling
         error_msg = f"Error de Ollama ({e.status_code}): {e.error}"
         # Log the detailed error if needed: print(f"Ollama ResponseError: {e}")
         return {"success": False, "summary": None, "error": error_msg}
    except Exception as e:
        # General error handling
        # Log the full error for debugging
        # import traceback
        # print(f"Unexpected error in analyze_dataframe_with_llm: {traceback.format_exc()}")
        return {"success": False, "summary": None, "error": f"Ocurrió un error inesperado durante el análisis de datos: {str(e)}"}

def read_uploaded_file(uploaded_file):
    """
    Lee un archivo subido (CSV o Excel) en un DataFrame de Pandas.
    """
    if uploaded_file is None:
        return None, "No se cargó ningún archivo."

    try:
        # Leer el contenido del archivo en memoria
        file_content = uploaded_file.getvalue()

        if uploaded_file.name.endswith('.csv'):
            # Intentar leer CSV, probando diferentes separadores comunes
            try:
                df = pd.read_csv(io.BytesIO(file_content), sep=None, engine='python', on_bad_lines='warn')
                return df, None
            except Exception as csv_e:
                 return None, f"Error al leer CSV: {csv_e}. Asegúrate que sea un CSV válido."

        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
             # Leer archivo Excel (requiere openpyxl)
            try:
                df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
                return df, None
            except Exception as excel_e:
                 return None, f"Error al leer Excel: {excel_e}. Asegúrate que sea un archivo Excel válido y tengas 'openpyxl' instalado."
        else:
            return None, "Formato de archivo no soportado. Por favor, sube un archivo CSV o Excel."

    except Exception as e:
        # import traceback
        # print(f"Error leyendo uploaded file: {traceback.format_exc()}")
        return None, f"Error inesperado al procesar el archivo: {e}"
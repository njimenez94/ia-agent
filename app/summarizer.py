import ollama
from website import Website, create_user_prompt

def get_system_prompt():
    """
    Returns the system prompt for the LLM
    """
    return "Eres un asistente que analiza el contenido de un sitio web y proporciona un resumen breve, \
            ignorando el texto que pueda estar relacionado con la navegación. \
            Responde en formato markdown en español."

def create_messages(website):
    """
    Create messages for the LLM
    
    Args:
        website (Website): Website object with content
        
    Returns:
        list: List of message dictionaries for the Ollama API
    """
    return [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": create_user_prompt(website)}
    ]

def summarize_website(url, model="llama3.2"):
    """
    Summarize a website using Ollama
    
    Args:
        url (str): URL of the website to summarize
        model (str, optional): Name of the Ollama model to use
        
    Returns:
        dict: Dictionary with summary and status information
    """
    try:
        website = Website(url)
        
        if not website.is_valid():
            return {
                "success": False,
                "summary": None,
                "error": website.error or "Failed to load website"
            }
        
        messages = create_messages(website)
        response = ollama.chat(model=model, messages=messages)
        
        return {
            "success": True,
            "summary": response["message"]["content"],
            "website_title": website.title,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "summary": None,
            "error": str(e)
        }
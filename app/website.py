import requests
from bs4 import BeautifulSoup

class Website:
    def __init__(self, url, headers=None):
        """
        Create a Website object from the given URL using BeautifulSoup
        
        Args:
            url (str): The URL of the website to analyze
            headers (dict, optional): HTTP headers for the request
        """
        self.url = url
        
        if headers is None:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            self.soup = BeautifulSoup(response.content, 'html.parser')
            self.title = self.soup.title.string if self.soup.title else "No title found"
            
            if self.soup.body:
                # Remove irrelevant elements
                for irrelevant in self.soup.body(["script", "style", "img", "input", "nav", "footer"]):
                    irrelevant.decompose()
                self.text = self.soup.body.get_text(separator="\n", strip=True)
            else:
                self.text = "No se pudo obtener el cuerpo del sitio web."
                
            self.status = "success"
            self.error = None
            
        except Exception as e:
            self.soup = None
            self.title = "Error"
            self.text = f"Error al acceder al sitio web: {str(e)}"
            self.status = "error"
            self.error = str(e)
    
    def show_soup(self):
        """
        Return the soup object
        """
        return self.soup
    
    def is_valid(self):
        """
        Check if the website was successfully loaded
        """
        return self.status == "success"

def create_user_prompt(website):
    """
    Create a prompt for the LLM based on website content
    
    Args:
        website (Website): Website object with content
        
    Returns:
        str: Formatted prompt for the LLM
    """
    user_prompt = f"Estás viendo un sitio web titulado {website.title}"
    user_prompt += "\nEl contenido de este sitio web es el siguiente; \
                    por favor proporciona un resumen breve de este sitio en formato markdown. \
                    Si incluye noticias o anuncios, resúmelos también.\n\n"
    user_prompt += website.text
    return user_prompt
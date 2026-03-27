import re
def formato_user(data):
    """
    Tareas:\n
    * No puede contener espacios en blanco
    * No puede contener numeros
    * Debe estar todo en minusculas
    """
    data = data.replace(" ", "")
    data = data.lower()
    data = re.sub(r'[^a-zA-Z0-9]', '', data)
    return data

# Chatbot Hospital Central

## Descripción

Este proyecto es un asistente médico virtual diseñado para el "Hospital Central" de Mendoza. Utiliza un modelo de lenguaje avanzado (Gemini) para responder consultas basándose en un manual médico (`manual_medico.pdf`). El chatbot está programado para ser empático, profesional y, lo más importante, seguro, derivando los casos de emergencia a atención médica inmediata.

## Características Principales

- **Asistente Virtual Médico:** Responde preguntas sobre temas médicos utilizando como fuente de conocimiento un documento PDF.
- **Interfaz Amigable:** Creado con Streamlit para una interacción sencilla a través de un chat.
- **Manejo de Emergencias:** Detecta síntomas de emergencia (como dolor de pecho, dificultad para respirar, etc.) e instruye al usuario para que busque ayuda de urgencia de inmediato.
- **Tono Profesional y Empático:** El asistente está configurado para comunicarse de manera cálida y profesional.
- **Privacidad:** No menciona explícitamente que su conocimiento proviene de un documento, actuando como un profesional informado.
- **Aviso Legal:** Incluye una advertencia clara de que no reemplaza la consulta médica profesional.

## Stack de Tecnologías

- **Lenguaje:** Python
- **Framework de la App:** Streamlit
- **Inteligencia Artificial:** Google Gemini
- **Gestión de dependencias:** pip

## Configuración e Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/tu_usuario/chatbot_HospitalCentral.git
    cd chatbot_HospitalCentral
    ```

2.  **Crear un entorno virtual e instalar dependencias:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configurar la API Key:**
    - Crea un archivo llamado `.env` en la raíz del proyecto.
    - Añade tu API Key de Gemini de la siguiente manera:
      ```
      GEMINI_API_KEY="TU_API_KEY_AQUI"
      ```

4.  **Asegúrate de tener el manual:**
    - El archivo `manual_medico.pdf` debe estar en la misma carpeta que `app.py`.

5.  **Ejecutar la aplicación:**
    ```bash
    streamlit run app.py
    ```

## Testing

Para verificar que el backend puede conectar con la API de Gemini y acceder al archivo PDF, puedes ejecutar el script de prueba:

```bash
python test_backend.py
```

Si todo está configurado correctamente, verás mensajes de éxito en la consola.

## Aviso Legal

Este asistente utiliza inteligencia artificial. La información proporcionada es solo orientativa y **no sustituye** una consulta médica profesional. En caso de una emergencia, contacta a los servicios de urgencia de inmediato.

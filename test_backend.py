# test_backend.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv() # Carga la API Key del .env

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: No se encontró GEMINI_API_KEY en las variables de entorno.")
    exit()

print(f"✅ API Key encontrada: {api_key[:5]}...")

# Configuración básica
genai.configure(api_key=api_key)

pdf_path = "manual_medico.pdf"

if not os.path.exists(pdf_path):
    print(f"❌ Error: No encuentro el archivo {pdf_path}")
    exit()

print("🚀 Subiendo PDF a Gemini (esto puede tardar unos segundos)...")
try:
    sample_file = genai.upload_file(pdf_path, mime_type="application/pdf")
    print(f"✅ Archivo subido exitosamente. URI: {sample_file.uri}")
    print("✅ Estado: El backend tiene acceso a la API y al archivo.")
except Exception as e:
    print(f"❌ Error al conectar con Gemini: {e}")

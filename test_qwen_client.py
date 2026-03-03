import os
import sys

# Asegúrate de que el directorio actual esté en PYTHONPATH
sys.path.insert(0, os.getcwd())

from qwen_client import QwenClient  # Cambia el nombre del archivo/clase si es distinto

def main():
    client = QwenClient()

    if not client.is_enabled():
        print("Error: DASHSCOPE_API_KEY no está configurada")
        print("Ejemplo de cómo configurarla:")
        print('  export DASHSCOPE_API_KEY="sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"')
        sys.exit(1)

    print(f"Modelo configurado: {client.model}")
    print(f"Base URL:         {client.base_url}")
    print(f"Max tokens:       {client.max_tokens}")
    print(f"Temperatura:      {client.temperature}\n")

    system_prompt = "Eres un asistente extremadamente útil y conciso."
    user_message  = "Dame 3 ventajas de usar Qwen3 frente a otros modelos grandes en 2026."

    print("Enviando consulta...\n")
    try:
        respuesta = client.chat(system_prompt, user_message)
        print("Respuesta del modelo:")
        print("-" * 60)
        print(respuesta)
        print("-" * 60)
    except Exception as e:
        print(f"Error al llamar a la API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

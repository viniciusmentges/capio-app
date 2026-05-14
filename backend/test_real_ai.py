import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.conf import settings
from services.ai import get_ai_service

def test_connection():
    print(f"--- VALIDANDO CONEXÃO REAL ---")
    print(f"USE_REAL_AI: {settings.USE_REAL_AI}")
    print(f"Model: {settings.ANTHROPIC_MODEL}")
    
    service = get_ai_service()
    print(f"Serviço instanciado: {type(service).__name__}")
    
    if type(service).__name__ != 'AnthropicAIService':
        print("ERRO: O serviço não é o AnthropicAIService. Verifique o .env")
        return

    try:
        print("\nSolicitando Exegese real para 'Salmo 23:1'...")
        res = service.explain_passage("Sl 23:1", "Salmo 23:1")
        
        print("\n--- RESPOSTA RECEBIDA ---")
        for key, value in res.items():
            print(f"[{key}]: {value[:100]}...")
            
        # Validar Constitution (Não deve ter !)
        text_full = " ".join(str(v) for v in res.values())
        if "!" in text_full:
            print("\nAVISO: A Constitution foi violada (encontrei '!')")
        else:
            print("\nSUCESSO: Constitution respeitada (sem '!')")
            
        print("\n--- CONEXÃO VALIDADA COM SUCESSO ---")
        
    except Exception as e:
        print(f"\nERRO NA CHAMADA REAL: {str(e)}")

if __name__ == "__main__":
    test_connection()

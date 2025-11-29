import asyncio
import os
from app.services.ai_service import AIService

async def test_ai():
    # Test with the provided API Key
    api_key = "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"
    print(f"Testing with API Key length: {len(api_key)}")
    
    service = AIService(api_key)
    
    # Test message
    mensaje = "necesito una lomiteria en asuncion"
    ciudad = "ASUNCION"
    barrio = "CENTRO"
    
    print(f"Interpreting: '{mensaje}'")
    try:
        resultado = await service.interpretar_mensaje(mensaje, ciudad, barrio)
        print("Result:", resultado)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai())

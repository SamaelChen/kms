"""Startup utilities for model downloading"""
import asyncio
import httpx
from app.config import settings


async def download_llm_model(max_retries: int = 3) -> bool:
    """Pull LLM model on startup to avoid first-query timeout"""
    url = f"{settings.OLLAMA_BASE_URL}/api/pull"
    model = settings.LLM_MODEL
    
    for attempt in range(max_retries):
        try:
            print(f"Pulling LLM model: {model} (attempt {attempt + 1}/{max_retries})")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={"name": model, "stream": False},
                    timeout=300.0
                )
                
                if response.status_code == 200:
                    print(f"LLM model '{model}' is ready")
                    return True
                else:
                    print(f"Failed to pull model: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"Error pulling model: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5 * (attempt + 1))
    
    print(f"Warning: Could not pull LLM model after {max_retries} attempts")
    print("Queries may timeout on first run. The model will be downloaded on first use.")
    return False

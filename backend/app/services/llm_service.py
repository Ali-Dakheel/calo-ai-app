"""
LLM Service - Ollama Integration
"""
import httpx
import json
from typing import AsyncGenerator, Dict, List, Optional
from app.config import get_settings

settings = get_settings()


async def check_ollama_health() -> bool:
    """Check if Ollama is running and accessible"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            return response.status_code == 200
    except Exception:
        return False


async def generate_completion(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> str:
    """
    Generate completion from Ollama
    
    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated text
    """
    if not await check_ollama_health():
        raise RuntimeError("Ollama is not running. Please start Ollama: 'ollama serve'")
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": settings.ollama_model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/chat",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        return result["message"]["content"]


async def generate_streaming_completion(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> AsyncGenerator[str, None]:
    """
    Generate streaming completion from Ollama
    
    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Yields:
        Text chunks as they're generated
    """
    if not await check_ollama_health():
        raise RuntimeError("Ollama is not running. Please start Ollama: 'ollama serve'")
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": settings.ollama_model,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
        async with client.stream(
            "POST",
            f"{settings.ollama_base_url}/api/chat",
            json=payload
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                    except json.JSONDecodeError:
                        continue


async def generate_structured_output(
    prompt: str,
    system_prompt: Optional[str] = None,
    output_schema: Optional[Dict] = None
) -> Dict:
    """
    Generate structured JSON output
    
    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        output_schema: Expected output schema
        
    Returns:
        Parsed JSON response
    """
    # Enhance system prompt to request JSON output
    json_instruction = "\nYou must respond with ONLY valid JSON. No additional text or explanation."
    enhanced_system = (system_prompt or "") + json_instruction
    
    if output_schema:
        enhanced_system += f"\nExpected schema: {json.dumps(output_schema)}"
    
    response = await generate_completion(
        prompt=prompt,
        system_prompt=enhanced_system,
        temperature=0.3  # Lower temperature for structured output
    )
    
    # Extract JSON from response
    try:
        # Try to parse directly
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        if "```json" in response:
            json_text = response.split("```json")[1].split("```")[0].strip()
            return json.loads(json_text)
        elif "```" in response:
            json_text = response.split("```")[1].split("```")[0].strip()
            return json.loads(json_text)
        else:
            raise ValueError(f"Could not parse JSON from response: {response}")


async def embed_text(text: str) -> List[float]:
    """
    Generate embeddings for text using Ollama
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector
    """
    if not await check_ollama_health():
        raise RuntimeError("Ollama is not running")
    
    payload = {
        "model": settings.ollama_model,
        "prompt": text
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/embeddings",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        return result["embedding"]

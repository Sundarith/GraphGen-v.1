import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load the environment variables from .env
load_dotenv(".env")

async def test_api():
    api_key = os.getenv("SYNTHESIZER_API_KEY")
    base_url = os.getenv("SYNTHESIZER_BASE_URL")
    model = os.getenv("SYNTHESIZER_MODEL", "gemini-1.5-flash")
    
    print(f"Testing Model: {model}")
    print(f"Testing Base URL: {base_url}")
    
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    print("\nSending 'Hello, are you there?' to Gemini...")
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello, are you there? Please reply with a short 'Yes'."}],
            max_tokens=50
        )
        print("\n=== SUCCESS ===")
        print(response.choices[0].message.content)
    except Exception as e:
        print("\n=== API ERROR ===")
        print(str(e))

if __name__ == "__main__":
    asyncio.run(test_api())


import asyncio
import httpx
from openai import AsyncOpenAI, APIStatusError

async def main():
    async with httpx.AsyncClient(
        trust_env=False,
        timeout=120.0,
    ) as http_client:
        ai = AsyncOpenAI(
            base_url="http://127.0.0.1:11434/v1",
            api_key="ollama",
            max_retries=0,
            http_client=http_client,
        )

        try:
            response = await ai.chat.completions.create(
                model="qwen2.5:3b",
                messages=[
                    {
                        "role": "user",
                        "content": "Привет! Ответь коротко.",
                    }
                ],
                max_tokens=100,
            )

            print("УСПЕХ:", response.choices[0].message.content)

        except APIStatusError as e:
            print("HTTP:", e.status_code)
            print("ТЕЛО ОШИБКИ:", e.response.text)

        except Exception as e:
            print("ОШИБКА:", repr(e))

        finally:
            await ai.close()

asyncio.run(main())
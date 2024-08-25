from player import Player
from openai import AsyncOpenAI

class PlayerGpt(Player):
    def __init__(self):
        super().__init__()
        # Get API Key at https://platform.openai.com/api-keys
        self.__openai_client = AsyncOpenAI(api_key='REPLACE_OPEN_AI_API_KEY')

    async def _request(self, prompt):
        response = await self.__openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    @property
    def name(self):
        return "GPT"

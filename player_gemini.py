import google.generativeai as genai
from player import Player

class PlayerGemini(Player):
    def __init__(self):
        super().__init__()
        # Get API key at: https://aistudio.google.com/app/apikey
        genai.configure(api_key='REPLACE_GOOGLE_AI_STUDIO_API_KEY')
        self.__gemini_client = genai.GenerativeModel('gemini-1.5-flash')

    async def _request(self, prompt):
        response = self.__gemini_client.generate_content(prompt)
        return response.text.strip()

    @property
    def name(self):
        return "Gemini"

from langchain_mistralai import ChatMistralAI

from config.settings import settings

mistral_llm = ChatMistralAI(
    model="mistral-medium-latest",
    api_key=settings.MISTRAL_API_KEY,
    temperature=0,
    max_retries=2,
    # other params...
)
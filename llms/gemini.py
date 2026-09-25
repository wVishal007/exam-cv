from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import settings

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    api_key=settings.GOOGLE_API_KEY,
    temperature=1.0,  # Gemini 3.0+ defaults to 1.0
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)
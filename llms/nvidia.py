from langchain_nvidia_ai_endpoints import ChatNVIDIA

from config.settings import settings

# Nemotron 3 Ultra - frontier reasoning and agentic workflows
nvidia_llm = ChatNVIDIA(
    model="nvidia/nemotron-3-ultra-550b-a55b",
    api_key=settings.NVIDIA_API_KEY,
)
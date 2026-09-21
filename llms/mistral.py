from langchain_mistralai import ChatMistralAI

mistral_llm = ChatMistralAI(
    model="mistral-medium-latest",
    temperature=0,
    max_retries=2,
    # other params...
)
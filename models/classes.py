from database.operations.llm_models import get_or_create_model

class BaseLLM:
    def __init__(self, model, name, provider):
        self.model = model
        self.name = name
        self.provider = provider
        self.model_id = None

    def register(self):
        self.model_id = get_or_create_model(
            provider=self.provider,
            name=self.name,
        )

        return self.model_id
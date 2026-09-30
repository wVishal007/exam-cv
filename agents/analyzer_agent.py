from llms.gemini import gemini
from models.structured_outputs import analyzer_output

analyzer_model = gemini.model.with_structured_output(
    analyzer_output
)
analyzer_model_id = gemini.model_id

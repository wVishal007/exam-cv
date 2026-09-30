from llms.gemini import gemini
from models.structured_outputs import rewrite_output

rewrite_model = gemini.model.with_structured_output(
    rewrite_output
)
rewrite_model_id = gemini.model_id
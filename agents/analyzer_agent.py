from llms.gemini import gemini_llm
from models.structured_outputs import analyzer_output
analyzer_model = gemini_llm.with_structured_output(analyzer_output)

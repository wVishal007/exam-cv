# from llms.mistral import mistral_llm
# from llms.nvidia import nvidia_llm
from llms.gemini import gemini_llm
from models.structured_outputs import rewrite_output


# rewrite_model = nvidia_llm.with_structured_output(rewrite_output)
rewrite_model = gemini_llm.with_structured_output(rewrite_output)

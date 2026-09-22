# main.py
# entry point for the project - for now just proving the abstraction layer works,
# this will become the real CLI once classification/routing logic is built

from llm_client import get_llm_response

response = get_llm_response("In one sentence, who is critiano ronaldo?")
print(response)
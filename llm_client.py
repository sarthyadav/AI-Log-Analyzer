# llm_client.py
# this file's whole job is: "given a prompt, return the LLM's text response"
# nothing else in my project should need to know whether that response came
# from a free local model or the real Claude API - this file hides that detail
#
# now using LangChain's chat model wrappers instead of calling ollama/anthropic
# directly - LangChain gives both providers the same .invoke() interface,
# so switching providers is just picking a different object, not different
# function calls like before

import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_anthropic import ChatAnthropic

load_dotenv()

# switching this one value is how I swap between free local testing and the
# real Claude API later - "ollama" for now since I have no API credits yet
LLM_PROVIDER = "ollama"


def _get_chat_model(temperature):
    """
    Returns a LangChain chat model object for whichever provider is
    currently configured. Both ChatOllama and ChatAnthropic expose the
    same .invoke() method, which is the whole point of using LangChain
    here - the rest of my code doesn't need to know which one it got.
    """
    if LLM_PROVIDER == "ollama":
        return ChatOllama(model="llama3.2", temperature=temperature)

    elif LLM_PROVIDER == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key is None:
            raise ValueError("ANTHROPIC_API_KEY not found - check your .env file")
        return ChatAnthropic(
            model="claude-sonnet-4-5",
            temperature=temperature,
            api_key=api_key
        )

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")


def get_llm_response(prompt, temperature=0.2):
    """
    Sends a prompt to whichever LLM provider is currently configured,
    and returns just the plain text response as a string.
    """
    chat_model = _get_chat_model(temperature)
    response = chat_model.invoke(prompt)
    return response.content
# llm_client.py
# this file's whole job is: "given a prompt, return the LLM's text response"
# nothing else in my project should need to know whether that response came
# from a free local model or the real Claude API - this file hides that detail

import os
import ollama
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

# switching this one value is how I swap between free local testing and the
# real Claude API later - "ollama" for now since I have no API credits yet
LLM_PROVIDER = "ollama"


def get_llm_response(prompt, temperature=0.2):
    """
    Sends a prompt to whichever LLM provider is currently configured,
    and returns just the plain text response as a string.

    temperature controls how random/creative the response is - lower
    values (closer to 0) give more consistent, repeatable answers, which
    matters a lot for tasks like classification where we need a reliable
    format every time. Defaults to 0.2 since most of what I ask this
    function to do needs to be consistent, not creative.
    """
    if LLM_PROVIDER == "ollama":
        return _call_ollama(prompt, temperature)
    elif LLM_PROVIDER == "claude":
        return _call_claude(prompt, temperature)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")


def _call_ollama(prompt, temperature):
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": temperature}
    )
    return response["message"]["content"]


def _call_claude(prompt, temperature):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key is None:
        raise ValueError("ANTHROPIC_API_KEY not found - check your .env file")

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
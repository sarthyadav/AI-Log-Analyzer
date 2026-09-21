# main.py
# switched to testing against a local Ollama model instead of the real Claude API,
# since I don't have API credits yet - this proves my prompt logic works for free,
# and I can swap in the real Claude call later without changing anything else

import ollama

# ollama.chat() sends a prompt to the locally running model and waits for
# the full response - no internet, no API key, no cost, since the model
# is running right here on my own machine
response = ollama.chat(
    model="llama3.2",
    messages=[
        {"role": "user", "content": "In one sentence, what does a CI/CD pipeline do?"}
    ]
)

# the response shape is a bit different from the Anthropic SDK - here the
# generated text lives at response['message']['content']
print(response["message"]["content"])
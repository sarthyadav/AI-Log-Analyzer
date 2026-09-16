# main.py
# sanity check: confirm my .env file is being read correctly and the API key loads
# NOTE: this file will get replaced with the real CLI logic soon - this is just
# to prove the secret-loading pipeline works before I build anything on top of it

import os
from dotenv import load_dotenv

# load_dotenv() reads the .env file and injects its key-value pairs into
# the environment variables for this running program
load_dotenv()

# os.getenv() reads an environment variable by name - returns None if it's not found
api_key = os.getenv("ANTHROPIC_API_KEY")

if api_key is None:
    print("No API key found. Did you create a .env file with ANTHROPIC_API_KEY set?")
else:
    # never print the actual key, even to my own terminal, even temporarily -
    # printing just the first few characters is enough to confirm it loaded correctly
    print(f"API key loaded successfully. Starts with: {api_key[:12]}...")
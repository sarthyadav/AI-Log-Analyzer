# main.py
# just a quick sanity check to make sure my venv + dependencies are wired up correctly
# before I start building the real CLI logic

from dotenv import load_dotenv

# load_dotenv() looks for a .env file in the project and loads any variables in it
# into the environment - we don't have a .env file yet, so this will just do nothing
# harmful for now, but it proves the import works
load_dotenv()

print("Environment is set up correctly. Ready to build the analyzer.")
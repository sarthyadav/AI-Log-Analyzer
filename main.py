# main.py
# entry point for the project - now classifying the log's failure type
# by asking the LLM to pick from a fixed set of categories

from llm_client import get_llm_response

VALID_CATEGORIES = ["compile error", "test failure", "timeout", "dependency issue"]


def read_log_file(file_path):
    """
    Reads the contents of a build log file and returns it as a string.
    """
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find log file at: {file_path}")


def classify_log(log_content):
    """
    Asks the LLM to classify the build failure into one of the fixed
    categories in VALID_CATEGORIES. Returns the category as a lowercase
    string, or "unknown" if the LLM didn't return a recognizable category.
    """
    categories_list = ", ".join(VALID_CATEGORIES)

    prompt = f"""You are analyzing a Jenkins build failure log.
Classify this failure into exactly ONE of these categories: {categories_list}

Respond with ONLY the category name, in lowercase, and nothing else.
Do not explain your reasoning. Do not add punctuation.

Log:
{log_content}
"""

    raw_response = get_llm_response(prompt)
    cleaned_response = raw_response.strip().lower()

    if cleaned_response in VALID_CATEGORIES:
        return cleaned_response
    else:
        return "unknown"


log_path = "sample_logs/compile_error.log"
log_content = read_log_file(log_path)

category = classify_log(log_content)
print(f"Detected failure category: {category}")
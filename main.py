# main.py
# entry point for the project - now accepts a log file path as a command
# line argument instead of a hardcoded path, and prints results cleanly

import argparse
from llm_client import get_llm_response

VALID_CATEGORIES = ["compile error", "test failure", "timeout", "dependency issue"]

CATEGORY_PROMPTS = {
    "compile error": """Focus on syntax errors, type mismatches, missing imports,
or misconfigured build files. Identify the exact line(s) causing the failure.""",

    "test failure": """Focus on which specific test(s) failed, the expected vs
actual values if shown, and whether this looks like a code bug or a flaky/
environment-dependent test.""",

    "timeout": """Focus on whether this looks like a resource constraint,
an infinite loop or deadlock, a slow external dependency, or a misconfigured
timeout threshold that's simply too short.""",

    "dependency issue": """Focus on version conflicts, missing packages,
registry/network failures, or incompatible dependency versions.""",
}


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

    raw_response = get_llm_response(prompt, temperature=0.0)
    cleaned_response = raw_response.strip().lower()

    if cleaned_response in VALID_CATEGORIES:
        return cleaned_response
    else:
        return "unknown"


def analyze_log(log_content, category):
    """
    Given a log and its classified category, asks the LLM for a root-cause
    analysis and a suggested fix, using a category-specific prompt.
    """
    if category not in CATEGORY_PROMPTS:
        category_instruction = "Analyze this build failure as best you can."
    else:
        category_instruction = CATEGORY_PROMPTS[category]

    prompt = f"""You are an experienced CI/CD engineer reviewing a Jenkins
build failure log. The failure has been classified as: {category}

{category_instruction}

Provide:
1. A brief root-cause explanation
2. A suggested fix

Be concise and specific. This is a recommendation for a human engineer to
review, not an instruction to be applied automatically.

Log:
{log_content}
"""

    return get_llm_response(prompt)


def print_report(file_path, category, analysis):
    """
    Prints a clean, readable report of the classification and analysis.
    Purely presentation - keeps formatting concerns separate from the
    actual classification/analysis logic above.
    """
    print("=" * 60)
    print(f"Jenkins Build Log Analysis: {file_path}")
    print("=" * 60)
    print(f"\nDetected Category: {category.upper()}\n")
    print("-" * 60)
    print(analysis)
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a Jenkins build failure log using an LLM."
    )
    parser.add_argument(
        "log_file",
        help="Path to the Jenkins build failure log file"
    )
    args = parser.parse_args()

    try:
        log_content = read_log_file(args.log_file)
    except FileNotFoundError as error:
        print(f"Error: {error}")
        return

    category = classify_log(log_content)
    analysis = analyze_log(log_content, category)

    print_report(args.log_file, category, analysis)

if __name__ == "__main__":
    main()
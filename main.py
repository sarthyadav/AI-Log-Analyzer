# main.py
# entry point for the project - now using LangChain's PromptTemplate to
# formally define prompts instead of building them with raw f-strings

import argparse
from langchain_core.prompts import PromptTemplate
from llm_client import get_llm_response

VALID_CATEGORIES = ["compile error", "test failure", "timeout", "dependency issue"]

CATEGORY_INSTRUCTIONS = {
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

# defining the classification prompt as a template with named placeholders,
# instead of a raw f-string - {categories_list} and {log_content} get filled
# in later via .format(), and LangChain validates that I actually provide
# every variable the template expects
CLASSIFICATION_PROMPT = PromptTemplate(
    input_variables=["categories_list", "log_content"],
    template="""You are analyzing a Jenkins build failure log.
Classify this failure into exactly ONE of these categories: {categories_list}

If the content does not look like a real build failure log at all, respond
with exactly: unrelated

Respond with ONLY the category name (or "unrelated"), in lowercase, and
nothing else. Do not explain your reasoning. Do not add punctuation.

Log:
{log_content}
"""
)

# same idea for the analysis prompt - this one has three variables since
# the category and its specific instruction both get plugged in
ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["category", "category_instruction", "log_content"],
    template="""You are an experienced CI/CD engineer reviewing a Jenkins
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
)


def read_log_file(file_path):
    """
    Reads the contents of a build log file and returns it as a string.
    Raises clear errors for missing files or empty content, rather than
    letting an empty log silently proceed into classification.
    """
    try:
        with open(file_path, "r") as file:
            content = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find log file at: {file_path}")

    if not content.strip():
        raise ValueError(f"Log file is empty: {file_path}")

    return content


def classify_log(log_content):
    """
    Asks the LLM to classify the build failure into one of the fixed
    categories in VALID_CATEGORIES, or "unrelated" if the content doesn't
    look like a real build log. Returns "unknown" only if the LLM's
    response doesn't match any expected value at all.
    """
    categories_list = ", ".join(VALID_CATEGORIES)

    prompt = CLASSIFICATION_PROMPT.format(
        categories_list=categories_list,
        log_content=log_content
    )

    raw_response = get_llm_response(prompt, temperature=0.0)
    cleaned_response = raw_response.strip().lower()

    if cleaned_response in VALID_CATEGORIES:
        return cleaned_response
    elif cleaned_response == "unrelated":
        return "unrelated"
    else:
        return "unknown"

def analyze_log(log_content, category):
    """
    Given a log and its classified category, asks the LLM for a root-cause
    analysis and a suggested fix, using a category-specific prompt.
    """
    if category == "unrelated":
        return ("This content does not appear to be a build failure log, "
                "so no analysis was performed.")

    if category not in CATEGORY_INSTRUCTIONS:
        category_instruction = "Analyze this build failure as best you can."
    else:
        category_instruction = CATEGORY_INSTRUCTIONS[category]

    prompt = ANALYSIS_PROMPT.format(
        category=category,
        category_instruction=category_instruction,
        log_content=log_content
    )

    return get_llm_response(prompt)


def print_report(file_path, category, analysis):
    """
    Prints a clean, readable report of the classification and analysis.
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
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        return

    try:
        category = classify_log(log_content)
        analysis = analyze_log(log_content, category)
    except ConnectionError as error:
        print(f"Error: {error}")
        return

    print_report(args.log_file, category, analysis)


if __name__ == "__main__":
    main()
# AI-Assisted Jenkins Build Log Analyzer

A Python command-line tool that reads a Jenkins build failure log, classifies
it into one of four categories (compile error, test failure, timeout,
dependency issue), then routes it to a category-specific prompt for a
root-cause explanation and a suggested fix.

Suggested fixes are recommendations for a human engineer to review. The tool
never applies anything automatically.

## How it works

1. Reads the log file from disk (with checks for missing or empty files).
2. Sends the log to an LLM with a constrained classification prompt at
   `temperature=0`, asking for exactly one category name. The prompt also
   allows an `unrelated` answer, so non-log input isn't forced into a category.
3. Normalizes the response (strips whitespace, lowercases) and validates it
   against the allowed categories. Anything unexpected becomes `unknown`.
4. Routes to a category-specific analysis prompt (for example, the timeout
   prompt focuses on slow dependencies and threshold settings, the test
   failure prompt on expected vs. actual values).
5. Prints a formatted report with the category, root cause, and suggested fix.

## Tech stack

- Python 3.13
- LangChain (`langchain-core` prompt templates, `langchain-ollama` and
  `langchain-anthropic` chat model wrappers)
- Ollama with `llama3.2` (local model, used for development and testing)
- Anthropic Claude API (supported as an alternative provider, see below)
- Jenkins (run locally to generate console logs)
- pytest
- python-dotenv

## Project structure

```
main.py            CLI entry point, prompts, classification and analysis logic
llm_client.py      Single get_llm_response() function that hides which LLM is used
tests/             pytest suite (LLM calls are mocked)
sample_logs/       Example failure logs for testing
pytest.ini         Points pytest at the project root
requirements.txt   Pinned dependencies
```

## Setup

1. Clone the repo and create a virtual environment:
```
   python -m venv venv
   venv\Scripts\Activate.ps1
```
2. Install dependencies:
```
   pip install -r requirements.txt
```
3. Install [Ollama](https://ollama.com) and pull the default model:
```
   ollama pull llama3.2
```

## Usage

```
python main.py <path-to-log-file>
```

Example:
```
python main.py sample_logs/jenkins_real_timeout.log
```

Errors are reported as short messages rather than tracebacks for: a missing
file, an empty file, and an unreachable Ollama service.

## LLM providers

The provider is set by `LLM_PROVIDER` in `llm_client.py`:

- `"ollama"` (default): runs locally, free, no API key needed.
- `"claude"`: uses the Anthropic API. Requires a `.env` file in the project
  root (never commit this file; it is listed in `.gitignore`):
```
  ANTHROPIC_API_KEY=your-key-here
```

Current status: the Claude integration is implemented and its connectivity
was verified (requests reach the API and authenticate), but it has not been
tested end to end because the account used for development has no credits.
All development and testing of the analysis output was done against the
local Ollama model.

## Sample logs

`sample_logs/` contains:

- Handwritten examples for each of the four categories.
- `jenkins_real_*.log`: console output from local Jenkins Freestyle jobs. The
  jobs run batch commands that print realistic error messages and exit with a
  non-zero code, so the logs have genuine Jenkins console formatting (workspace
  paths, "Started by user", "Finished: FAILURE") around simulated failures.
- `empty.log` and `not_a_log.log` for edge-case testing.

## Tests

```
pytest
```

The suite covers log file reading (valid, missing, empty) and classification
parsing (valid category, messy formatting, `unrelated`, unexpected output).
The LLM call is mocked, so tests are fast and don't need Ollama running.
End-to-end behavior was checked manually against the sample logs.

## Design notes

- **Swappable LLM backend**: `llm_client.py` exposes one function, so the rest
  of the code doesn't depend on which provider is used. This allowed
  development against a free local model.
- **Temperature 0 for classification**: an early version with the default
  temperature classified the same log differently across runs. Setting it to 0
  made results consistent.
- **Escape hatch in the prompt**: with only four allowed categories, the model
  forced unrelated text into "test failure". Adding an `unrelated` option fixed
  this.
- **Output validation**: LLM output is never trusted as-is; it is normalized and
  checked against the allowed set before use.
- **Human in the loop**: suggestions are framed as recommendations, since LLM
  output can be wrong.

## Limitations

- Small local models can produce vague or inaccurate analysis text.
- Only four failure categories are supported.
- Logs are sent to the model in full, so very large logs may exceed its context
  window.
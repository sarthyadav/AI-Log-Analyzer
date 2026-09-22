# main.py
# entry point for the project - now reading a real log file from disk
# instead of using a hardcoded question

from llm_client import get_llm_response


def read_log_file(file_path):
    """
    Reads the contents of a build log file and returns it as a string.
    Raises a clear error if the file doesn't exist, rather than letting
    Python's default error message (which can be confusing) bubble up.
    """
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find log file at: {file_path}")


log_path = "sample_logs/compile_error.log"
log_content = read_log_file(log_path)

print("--- Log file loaded ---")
print(log_content)
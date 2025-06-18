def load_prompt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# Load the prompt
prompt_template = load_prompt("../chains/prompt.txt")

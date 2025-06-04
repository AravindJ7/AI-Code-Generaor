import autopep8
import subprocess
import tempfile
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import io
import sys

model_name = "Salesforce/codegen-350M-multi"

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(model_name)
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

def generate_code(prompt: str) -> str:
    full_prompt = f"# Python function to {prompt}\ndef"
    inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=256).to(device)
    outputs = model.generate(
        inputs.input_ids,
        max_length=512,
        do_sample=False,       # Use greedy decoding for faster and more consistent output
        pad_token_id=tokenizer.eos_token_id
    )
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    generated_code = result[len(full_prompt):].strip()

    # Cut off extra functions if multiple defs generated (optional)
    if 'def' in generated_code:
        last_def = generated_code.find('def', 1)  # find second 'def'
        if last_def != -1:
            generated_code = generated_code[:last_def].strip()

    return generated_code

def format_code(code: str) -> str:
    try:
        return autopep8.fix_code(code)
    except Exception as e:
        return f"Formatting error: {str(e)}"

def analyze_code(code: str) -> str:
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as f:
        f.write(code)
        path = f.name
    try:
        result = subprocess.run(
            ['pylint', '--disable=all', '--enable=E,W,C,R', path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout.strip()
        if not output:
            output = "No issues found by pylint."
        return output
    finally:
        os.unlink(path)

def execute_code(code: str) -> str:
    # Capture stdout and stderr from exec
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = io.StringIO()
    sys.stdout = redirected_output
    sys.stderr = redirected_output

    try:
        exec_globals = {}
        exec(code, exec_globals)
        output = redirected_output.getvalue()
        if not output:
            output = "Execution completed with no output."
        return output
    except Exception as e:
        return f"Execution error: {e}"
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


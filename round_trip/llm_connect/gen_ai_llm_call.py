import concurrent.futures
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from functools import partial

import dotenv

# Determine the directory of the current file
current_dir = os.path.dirname(__file__)

# Construct the path to the root directory assuming the structure is known
# If this file is - root/project/module/your_module.py, you want to go up two levels
project_root = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))

# Construct the .env file path
dotenv_path = os.path.join(project_root, '.env')
print(dotenv_path)

# Load environment variables
dotenv.load_dotenv(dotenv_path=dotenv_path)


from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.proxy.native.google_vertexai.clients import GenerativeModel
from gen_ai_hub.proxy.native.openai import chat

CALL_TIMEOUT_SECONDS = 120
MAX_RETRIES = 2


import signal

def timeout_handler(signum, frame):
    raise TimeoutError()

def generate_gemini_with_timeout(system_prompt, examples, user_prompt, temperature, response_format=True):
    """Call generate_gemini with a timeout, retry once if timed out."""
    max_retries = 1
    retry_count = 0

    while retry_count < max_retries:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(CALL_TIMEOUT_SECONDS)
        try:
            result = generate_gemini(system_prompt, examples, user_prompt, temperature, response_format)
            signal.alarm(0)  # disable alarm
            return result
        except TimeoutError:
            print("generate_gemini call timed out. Retrying...")
            retry_count += 1
        except Exception as ex:
            print(f"An unexpected error occurred: {ex}. Proceeding to next iteration.")
            return None

    print("Max retries exceeded. Proceeding to next iteration.")
    return None

def generate_gpt_with_timeout(system_prompt, user_prompt, assistant_prompt, prompt, temperature, response_format=True):
    """Call generate_gemini with a timeout, retry once if timed out."""
    max_retries = 1
    retry_count = 0

    while retry_count < max_retries:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(CALL_TIMEOUT_SECONDS)
        try:
            result = generate_gpt(system_prompt, user_prompt, assistant_prompt, prompt, temperature, response_format)
            signal.alarm(0)  # disable alarm
            return result
        except TimeoutError:
            print("generate_gpt call timed out. Retrying...")
            retry_count += 1
        except Exception as ex:
            print(f"An unexpected error occurred: {ex}. Proceeding to next iteration.")
            return None

    print("Max retries exceeded. Proceeding to next iteration.")
    return None

def generate_gemini(system_prompt, examples, user_prompt, temperature, response_format=True):

    proxy_client = get_proxy_client("gen-ai-hub")
    system_prompt = f"""
    {system_prompt}
    Here's an example:
    {examples}
        """
    model = GenerativeModel(
        proxy_client=proxy_client,
        model_name="gemini-1.5-pro",
        system_instruction=[system_prompt],
    )

    content = [{"role": "user", "parts": [{"text": user_prompt}]}]
    if response_format:
        config = {"max_output_tokens": 8000, "temperature": temperature, "response_mime_type": "application/json"}
    else:
        config = {"max_output_tokens": 8000, "temperature": temperature}

    response = model.generate_content(content, generation_config=config)
    return response.text


def generate_gpt(system_prompt, user_prompt, assistant_prompt, prompt, temperature, response_format=True):

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": assistant_prompt},
        {"role": "user", "content": prompt},
    ]
    if response_format:

        kwargs = dict(
            model_name="gpt-4o",
            messages=messages,
            temperature=temperature,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )
    else:
        kwargs = dict(
            model_name="gpt-4o",
            messages=messages,
            temperature=temperature,
            max_tokens=4000,
        )
    response = chat.completions.create(**kwargs)

    return response.choices[0].message.content
# from src.t2m.prompt_engineering import mermaid, graphviz, json_format
# from src.llm_connect.ask_open_ai import ask_gpt
import json



def generate_prompt_gemini(path_to_json, path_to_text, bpmn_desc):


    with open(path_to_json, "r") as output_file:
        output_json = json.load(output_file)

    with open(path_to_text, "r") as input_file:
        input_description = input_file.read().strip()

    system_prompt = (
        f"You are a BPMN expert. Generate accurate BPMN2.0 models in the form of json from the given textual descriptions. "
        f"if an elemnt does not exist in the description, output an empty list for it. "
        f"follow these guidlines below to ensure consistency and accuracy: {bpmn_desc}. "
        f"Here is an example, follow the logic of the example:"

    )

    examples = [f"input: {input_description}, output: {output_json}"]

    return system_prompt, examples

def generate_prompt_gpt(path_to_json, path_to_text, bpmn_desc):


    with open(path_to_json, "r") as output_file:
        output_json = json.load(output_file)

    with open(path_to_text, "r") as input_file:
        input_description = input_file.read().strip()

    system_prompt = (
        f"You are a BPMN expert. Generate accurate BPMN2.0 models in the form of json from the given textual descriptions. "
        f"if an elemnt does not exist in the description, output an empty list for it. "
        f"follow these guidlines below to ensure consistency and accuracy: {bpmn_desc}. "
        f"Here is an example, follow the logic of the example:"

    )

    user_prompt, assistant_prompt = f"{input_description}", f"{output_json}"

    return system_prompt, user_prompt, assistant_prompt

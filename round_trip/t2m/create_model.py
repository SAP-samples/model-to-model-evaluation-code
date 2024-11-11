# from src.t2m.prompt_engineering import mermaid, graphviz, json_format
# from src.llm_connect.ask_open_ai import ask_gpt
import json

# """ prompt for model generation """
# def create_prompt(description,set_of_rules,graph_type="mermaid.js"):
#     prompt = "Process description: {}. {}. Considering provided process description and a set of custom rules create a valid {} graph.".format(description,set_of_rules,graph_type)
#     prompt += "Only a valid graph without any additional text or information must be returned."
#     if graph_type == "mermaid.js":
#         prompt += "It is also prohibeted to return mermaid diagram with ```mermaid ``` notation!!!"
#     return prompt

# """ call llm to generate model """
# def generate_model(model,description,graph_type="mermaid.js"):
#     try:
#         if "mermaid" in graph_type:
#             set_of_rules = mermaid
#         else:
#             set_of_rules = graphviz
#         prompt = create_prompt(description,set_of_rules,graph_type)
#         response = ask_gpt(model,prompt)
#         if "```mermaid" in response:
#             response = response[response.find('\n')+1:response.rfind('\n')]
#         return response
#     except Exception as e:
#         return e

# """ call llm to generate json bpmn 2.0 model """
# def generate_json_model(model,description):
#     try:
#         prompt = "Consider following process description:{} Convert this process description into json bpmn 2.0 model using this rules. {}".format(description,json_format)
#         response = ask_gpt(model,prompt)
#         return response
#     except Exception as e:
#         return e

######################################################################

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

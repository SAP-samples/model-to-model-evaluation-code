# from llm_connect.ask_models import ask_gpt
from src.m2t.prompt_engineering import bpmn_desc
import json

# """ prompt for process description generation """
# def create_prompt(process_model,graph_type="mermaid.js",elref=1):
#     if elref == 0:
#         prompt = "Read this {} model: {}. Convert this model to a textual process description using simple natural language. Return only text summary".format(graph_type,process_model)
#     else:
#         prompt = "Read this {} model: {}. Convert this model to a textual process description using simple natural language without mentioning types of the model elements (i.e., task, startevent, endevent,gateway, etc.). Return only text summary".format(graph_type,process_model)
#     return prompt

# """ call llm to generate process description out of model """
# def generate_description(model,process_model,graph_type="mermaid.js",elref=1):
#     try:
#         prompt = create_prompt(process_model,graph_type,elref)
#         response = ask_gpt(model,prompt)
#         return response
#     except Exception as e:
#         return e

# """ call llm to generate process description out of model """
# def generate_description_from_json(model,process_model):
#     try:
#         prompt = "Consider following process model in json format based on BPMN2.0 Standard. {}. Generate a natural language description of the process depicted in the following BPMN2.0 JSON without mentioning types of the model elements (i.e., task, startevent, endevent,gateway, etc.). Return plain text as a summary about the process.".format(process_model)
#         response = ask_gpt(model, prompt)
#         return response
#     except Exception as e:
#         return e

######################################################################

def generate_prompt_gemini(path_to_json, path_to_text, bpmn_desc):


    with open(path_to_json, "r") as input_file:
        input_json = json.load(input_file)

    with open(path_to_text, "r") as output_file:
        output_description = output_file.read().strip()

    # system_prompt = (
    #     f"You are a BPMN expert. Generate the textual description "
    #     f"for a given BPMN model. You can read the information about the elements from "
    #     f"here: {bpmn_desc}, do not mention the types of the elements and return explicit plain text, "
    #     f"true to the model."
    # )
    system_prompt = (
    f"You are a BPMN expert. Describe the BPMN model in detail, focusing specifically on the sequence of actions, "
    f"interactions between entities, and any necessary conditions or parallel processes. Additionally, include the "
    f"specific tasks and events that are part of the model to ensure explicit detail for model reconstruction. "
    f"Avoid technical jargon, and instead, offer a thorough narrative of the process flow. "
    f"Use clear references to decisions and repeating actions, while outlining the starting and ending points. "
    f"I will provide you with an example, please follow the logic in the example when generating text. ")

        # # Alternative:
    # system_prompt = (
    #     """
    #     You are an expert in bpmn2.0 and know all the usual elements.
    #     For an input BPMN model in json format, output textual description that is coherent and explicit.
    #     keep the order of events and activities and describe them sentence by sentence in the order of appearance.
    #     If there are steps that are run in parallel, mention those explicitely.
    #     if there are distinct participants/organisations (pools and lanes),
    #     show the flow of events and activities underneath the label of that relevant participant.
    #     Avoid technical jargons. I will provide you with an example, please follow the logic in the example when generating text.
    #     """)

    examples = [f"input: {input_json}, output: {output_description}"]

    return system_prompt, examples

def generate_prompt_gpt(path_to_json, path_to_text, bpmn_desc):


    with open(path_to_json, "r") as input_file:
        input_json = json.load(input_file)

    with open(path_to_text, "r") as output_file:
        output_description = output_file.read().strip()

    # system_prompt = (
    # f"You are a BPMN expert. Generate the textual description "
    # f"for a given BPMN model. You can read the information about the elements from "
    # f"here: {bpmn_desc}, do not mention the types of the elements and return explicit and accurate plain text, "
    # f"true to the model. Here is an example: "
    #     )
    system_prompt = (
        f"You are a BPMN expert. Describe the BPMN model in detail, focusing specifically on the sequence of actions, "
        f"interactions between entities, and any necessary conditions or parallel processes. Additionally, include the "
        f"specific tasks and events that are part of the model to ensure explicit detail for model reconstruction. "
        f"Avoid technical jargon, and instead, offer a thorough narrative of the process flow. "
        f"Use clear references to decisions and repeating actions, while outlining the starting and ending points. "
        f"I will provide you with an example, please follow the logic in the example when generating text. ")

    # # Alternative:
    # system_prompt = (
    #     """
    #     You are an expert in bpmn2.0 and know all the usual elements.
    #     For an input BPMN model in json format, output textual description that is coherent and explicit.
    #     keep the order of events and activities and describe them sentence by sentence in the order of appearance.
    #     If there are steps that are run in parallel, mention those explicitely.
    #     if there are distinct participants/organisations (pools and lanes),
    #     show the flow of events and activities underneath the label of that relevant participant.
    #     Avoid technical jargons. I will provide you with an example, please follow the logic in the example when generating text.
    #     """)


    user_prompt, assistant_prompt = f"{input_json}", f"{output_description}"

    return system_prompt, user_prompt, assistant_prompt



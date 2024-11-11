import os, sys
import json
import logging
import argparse
import csv

sys.path.append("./data/")
sys.path.append("./model_evaluation")
sys.path.append("./round_trip")

import bpmn_similarity
from text_evaluation import text_similarity

from round_trip.llm_connect.gen_ai_llm_call import generate_gemini_with_timeout
from round_trip.m2t.create_description import generate_prompt_gemini as generate_prompt_gemini_m2t
from round_trip.m2t.prompt_engineering import bpmn_desc
from round_trip.t2m.create_model import generate_prompt_gemini as generate_prompt_gemini_t2m
from round_trip.t2m.prompt_engineering import json_desc, json_desc_2, json_format


def main_m2m(model_path, text_path):
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
        # handlers=[logging.FileHandler("script_log.log"), logging.StreamHandler()]
    )
    logger = logging.getLogger("GeminiLogger")


    if args.example == 'pet':
        path_to_json = "./data/prompt_ex_json_pet.json"
        path_to_text = "./data/prompt_ex_text_pet.txt"
    else:
        path_to_json = "./data/prompt_ex_json_real_set.json"
        path_to_text = "./data/prompt_ex_text_real_set.txt"

    system_prompt_gemini_m2t, examples_m2t = generate_prompt_gemini_m2t(path_to_json, path_to_text, bpmn_desc)
    system_prompt_gemini_t2m, examples_t2m = generate_prompt_gemini_t2m(path_to_json, path_to_text, json_desc)

    # print("M2T prompts:")
    # print(system_prompt_gemini_m2t, examples_m2t)

    # print("T2M prompts:")
    # print(system_prompt_gemini_t2m, examples_t2m)

    t2t_eval_1 = {}
    t2t_eval_2 = {}
    m2m_eval_1 = {}
    m2m_eval_2 = {}
    temp_in = 1
    temp_out = 0

    model_files = os.listdir(model_path)
    logger.info('Starting the processing of models and texts')

    for i, model_file in enumerate(model_files):  # Use enumerate for progress tracking
        logger.info(f'Processing file: {model_file}')
        try:
            with open(os.path.join(model_path, model_file), "r") as infile:
                model = json.load(infile)

            with open(os.path.join(text_path, model_file.replace(".json", ".txt")), "r") as file:
                description = file.read()

            text_eval_1 = []
            text_eval_2 = []
            model_eval_1 = []
            model_eval_2 = []

            for j in range(3):
                logger.info(f'Iteration {j + 1} for file: {model_file}')
                gen_text = generate_gemini_with_timeout(
                    system_prompt_gemini_m2t,
                    examples_m2t,
                    "Here is the model: " + str(model),
                    temp_in,
                    response_format=False
                )
                if gen_text is None:
                    logger.info(f'Skipping iteration {j + 1} due to timeout for file: {model_file}')
                    continue

                gen_model = generate_gemini_with_timeout(
                    system_prompt_gemini_t2m,
                    examples_t2m,
                    "Here is the textual description: " + gen_text,
                    temp_out,
                    response_format=True
                )

                if gen_model is None:
                    logger.info(f'Skipping iteration {j + 1} due to timeout for file: {model_file}')
                    continue

                try:
                    text_eval_1.append(text_similarity.sts_bert(description, gen_text))
                    text_eval_2.append(text_similarity.text_similarity_alternative(description, gen_text, threshold=0.8))
                    model_eval_1.append(
                        bpmn_similarity.calculate_similarity_scores(
                            model, json.loads(gen_model), method="dice", similarity_threshold=0.8
                        )[0]["overall"]
                    )
                    model_eval_2.append(
                        bpmn_similarity.calculate_similarity_alternative(
                            model, json.loads(gen_model), method="dice", similarity_threshold=0.8
                        )["overall"]
                    )
                except Exception as e:
                    logger.error(f"Error during calculations in iteration {j + 1} for file {model_file}: {e}")
                    continue

            if text_eval_1:
                t2t_eval_1[model_file] = sum(text_eval_1) / len(text_eval_1)

            if text_eval_2:
                t2t_eval_2[model_file] = sum(text_eval_2) / len(text_eval_2)

            if model_eval_1:
                m2m_eval_1[model_file] = sum(model_eval_1) / len(model_eval_1)

            if model_eval_2:
                m2m_eval_2[model_file] = sum(model_eval_2) / len(model_eval_2)

        except Exception as e:
            logger.error(f"An error occurred while processing file {model_file}: {e}")


    logger.info('Completed processing all models and texts')

    # Write results to CSV
    with open('./'+'gemini' + args.example + args.direction + '.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['model_name', 't2t_eval_1','t2t_eval_2', 'm2m_eval_1', 'm2m_eval_2'])  # Header

        for model_name in model_files:
            csv_writer.writerow([
                model_name,
                t2t_eval_1.get(model_name, 'N/A'),
                t2t_eval_2.get(model_name, 'N/A'),
                m2m_eval_1.get(model_name, 'N/A'),
                m2m_eval_2.get(model_name, 'N/A')
            ])

def main_t2t(model_path, text_path):
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger("GeminiLogger")


    if args.example == 'pet':
        path_to_json = "./data/prompt_ex_json_pet.json"
        path_to_text = "./data/prompt_ex_text_pet.txt"
    else:
        path_to_json = "./data/prompt_ex_json_real_set.json"
        path_to_text = "./data/prompt_ex_text_real_set.txt"

    system_prompt_gemini_m2t, examples_m2t = generate_prompt_gemini_m2t(path_to_json, path_to_text, bpmn_desc)
    system_prompt_gemini_t2m, examples_t2m = generate_prompt_gemini_t2m(path_to_json, path_to_text, json_desc)

    t2t_eval_1 = {}
    t2t_eval_2 = {}
    m2m_eval_1 = {}
    m2m_eval_2 = {}
    temp_in = 1
    temp_out = 0

    model_files = os.listdir(model_path)
    logger.info('Starting the processing of models and texts')

    for i, model_file in enumerate(model_files):  # Use enumerate for progress tracking
        logger.info(f'Processing file: {model_file}')
        try:
            with open(os.path.join(model_path, model_file), "r") as infile:
                model = json.load(infile)

            with open(os.path.join(text_path, model_file.replace(".json", ".txt")), "r") as file:
                description = file.read()

            text_eval_1 = []
            text_eval_2 = []
            model_eval_1 = []
            model_eval_2 = []

            for j in range(3):
                logger.info(f'Iteration {j + 1} for file: {model_file}')
                gen_model = generate_gemini_with_timeout(
                    system_prompt_gemini_t2m,
                    examples_t2m,
                    "Here is the texual description: " + str(description),
                    temp_in,
                    response_format=True
                )

                if gen_model:
                    print(json.loads(gen_model)['pools'])
                if gen_model is None:
                    logger.info(f'Skipping iteration {j + 1} due to timeout for file: {model_file}')
                    continue

                gen_text = generate_gemini_with_timeout(
                    system_prompt_gemini_m2t,
                    examples_m2t,
                    "Here is the model: " + str(gen_model),
                    temp_out,
                    response_format=False
                )
                if gen_text is None:
                    logger.info(f'Skipping iteration {j + 1} due to timeout for file: {model_file}')
                    continue

                try:
                    text_eval_1.append(text_similarity.sts_bert(description, gen_text))
                    text_eval_2.append(text_similarity.text_similarity_alternative(description, gen_text, threshold=0.8))
                    model_eval_1.append(
                        bpmn_similarity.calculate_similarity_scores(
                            model, json.loads(gen_model), method="dice", similarity_threshold=0.8
                        )[0]["overall"]
                    )
                    model_eval_2.append(
                        bpmn_similarity.calculate_similarity_alternative(
                            model, json.loads(gen_model), method="dice", similarity_threshold=0.8
                        )["overall"]
                    )
                except Exception as e:
                    logger.error(f"Error during calculations in iteration {j + 1} for file {model_file}: {e}")
                    continue

            if text_eval_1:
                t2t_eval_1[model_file] = sum(text_eval_1) / len(text_eval_1)

            if text_eval_2:
                t2t_eval_2[model_file] = sum(text_eval_2) / len(text_eval_2)

            if model_eval_1:
                m2m_eval_1[model_file] = sum(model_eval_1) / len(model_eval_1)

            if model_eval_2:
                m2m_eval_2[model_file] = sum(model_eval_2) / len(model_eval_2)

        except Exception as e:
            logger.error(f"An error occurred while processing file {model_file}: {e}")


    logger.info('Completed processing all models and texts')

    # Write results to CSV
    with open('./'+'gemini' + args.example + args.direction + '.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['model_name', 't2t_eval_1','t2t_eval_2', 'm2m_eval_1', 'm2m_eval_2'])  # Header

        for model_name in model_files:
            csv_writer.writerow([
                model_name,
                t2t_eval_1.get(model_name, 'N/A'),
                t2t_eval_2.get(model_name, 'N/A'),
                m2m_eval_1.get(model_name, 'N/A'),
                m2m_eval_2.get(model_name, 'N/A')
            ])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process models and text with retries and timeout.")
    parser.add_argument('--model-path', type=str, required=True, help='Path to the models directory')
    parser.add_argument('--text-path', type=str, required=True, help='Path to the text descriptions directory')
    parser.add_argument('--example', type=str, required=True, help='pet or real_set')
    parser.add_argument('--direction', type=str, required=True, help='m2m or t2t')

    args = parser.parse_args()
    if args.direction == 'm2m':
        main_m2m(args.model_path, args.text_path)
    elif args.direction == 't2t':
        main_t2t(args.model_path, args.text_path)








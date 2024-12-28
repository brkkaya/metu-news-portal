import os
import json
import time
from tqdm import tqdm
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import jsonlines
import traceback
import langid
from langchain_together import ChatTogether
from langchain_nvidia_ai_endpoints import ChatNVIDIA


# Function to write to JSONL file
def write_to_file(responses, filename="summarization.jsonl"):
    with open(filename, "a", encoding="utf-8") as file:
        file.write(json.dumps(responses, ensure_ascii=False) + "\n")


# Function to process data in batches
def process_data(start_index, data, write_path, question_chain, question_chain_tr):
    responses_rest = []
    responses = []
    try:
        for i in tqdm(
            range(start_index, len(data)), total=len(data), initial=start_index
        ):
            title = data[i]["title"]

            body = ""
            if "body" not in data[i]:
                body = data[i]["text"]
            else:
                body = data[i]["body"]

            if len(body.split()) > 10000:
                print(
                    f"Too long text for {i} with {len(body.split())} words, skipping."
                )
                continue

            excerpt = ""
            if "excerpt" in data[i]:
                excerpt = data[i]["excerpt"]

            ctx = f"{title}\n\n{excerpt}\n{body}"

            current_chain = question_chain
            if langid.classify(body)[0] == "tr":
                current_chain = question_chain_tr

            if "validated" not in data[i] or data[i]["validated"] != "Ok":
                try:
                    question = current_chain.invoke(ctx)
                    write_line = data[i]
                    write_line["question"] = ctx
                    write_line["answer"] = question
                    write_to_file(write_line, write_path)
                except Exception as e:
                    responses.extend(responses_rest)
                    responses_rest = []
                    print(f"Error with context {ctx} at index {i}: {e}")
                    time.sleep(15)
                    raise e
                else:
                    responses_rest.append(question)
            else:
                write_line = data[i]
                write_to_file(write_line, write_path)

    except Exception as e:
        print(f"Fatal exception in process data: {e}")
        traceback.print_exc()


def main():
    together_api_key = os.environ.get("together-api-key", "no-key")
    # Model Configuration
    llm = ChatTogether(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        api_key=together_api_key,
    )

    llm_tr = ChatTogether(
        model="Qwen/Qwen2.5-7B-Instruct-Turbo",
        api_key=together_api_key,
    )

    # Prompt Template Definition
    question_prompt = PromptTemplate(
        input_variables=["context"],
        template="""
        You are an expert in news summarization. Given the following news, summarize it in a few sentences. Just write the summary and nothing else:
        News Article: {context}
        Answer: # summary here
        """,
    )
    question_prompt_tr = PromptTemplate(
        input_variables=["context"],
        template="""
        Sen haber özeti oluşturan bir uzmansın. Aşağıdaki haberi birkaç cümle ile özetle. Sadece haber özetini ver:
        Haber: {context}
        Özet:
        """,
    )
    # Create the LLM Chain
    question_chain = question_prompt | llm | StrOutputParser()
    question_chain_tr = question_prompt_tr | llm_tr | StrOutputParser()

    target_datasets = [
        "games_summary_regex.jsonl",
        "metu_scrape_summary_regex.jsonl",
        "news_summary_regex.jsonl",
        "yeni_cnbc_sanat_summary_regex.jsonl",
        "yeni_economist_bilim_summary_regex.jsonl",
        "yeni_guardian_sanat_summary_regex.jsonl",
        "yeni_sciencenews_bilim_summary_regex.jsonl",
        "yeni_webtekno_bilim_summary_regex.jsonl",
    ]
    target_file_names = [
        file_name.replace("_regex.jsonl", "_fixed.jsonl")
        for file_name in target_datasets
    ]
    scrape_root = "summaries_regex"
    summary_root = "summaries_fixed"

    if not os.path.exists(summary_root):
        os.makedirs(summary_root)

    for dataset, target_name in zip(target_datasets, target_file_names):
        print(f"Start processing {dataset}")

        write_path = os.path.join(summary_root, target_name)
        dataset_path = os.path.join(scrape_root, dataset)

        with jsonlines.open(dataset_path) as jsonl_f:
            data = [obj for obj in jsonl_f]
            if len(data) > 1500:
                data = data[0:1500]
        data_len = len(data)

        if "answer" in data[0]:
            print(
                f"{dataset} already has summarizations, treating this as a refinement step."
            )
            data = detect_dataset_problems(data)
            validated_count = sum(1 for elem in data if elem["validated"] == "Ok")
            print(
                f"For dataset {dataset} validation ratio is : {validated_count}/{len(data)}"
            )
            print(
                f"-- Language mismatch count : {sum(1 for elem in data if elem['validated'] == 'Language mismatch')}"
            )
            print(
                f"-- Problematic start count : {sum(1 for elem in data if elem['validated'] == 'Problematic start')}"
            )
            print("")

        if not os.path.exists(write_path):
            with open(write_path, "w+") as f:
                pass

        # Loop to retry in errors
        for _ in range(100):
            try:
                line_count = 0
                try:
                    with open(write_path, "rb") as f:
                        line_count = sum(1 for _ in f)
                except:
                    print(
                        f"Previous write does not exist for {dataset}, start from index 0."
                    )

                print(f"At {line_count}/{data_len} of {dataset}")

                process_data(
                    line_count, data, write_path, question_chain, question_chain_tr
                )
            except Exception as e:
                print(f"Problem in processing, will retry for {dataset}")

            else:
                print(f"Finished processing {dataset}")
                break


def json_to_jsonl(json_file, jsonl_file):
    with open(json_file, "r") as f:
        json_data = json.load(f)

    with jsonlines.open("output.jsonl", "w") as writer:
        writer.write_all(json_data)


def detect_language(text, question):
    text_detect = langid.classify(text)
    question_detect = langid.classify(question)
    return text_detect[0] != question_detect[0]


def detect_problematic_start(text):
    if text.startswith("Here"):
        return True
    return False


def detect_problems(text, question):
    if detect_problematic_start(text):
        return "Problematic start"
    if detect_language(text, question):
        return "Language mismatch"
    return "Ok"


def detect_dataset_problems(dataset):
    for elem in dataset:
        elem["validated"] = detect_problems(elem["answer"], elem["question"])

    return dataset


if __name__ == "__main__":
    main()

import langid
import re
import json
import jsonlines
import os


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


files = list(os.listdir("summaries_fixed"))

file_root = "summaries_fixed"

for dataset in files:
    dataset_path = os.path.join(file_root, dataset)
    with jsonlines.open(dataset_path) as jsonl_f:
        data = [obj for obj in jsonl_f]

    data = detect_dataset_problems(data)
    validated_count = sum(1 for elem in data if elem["validated"] == "Ok")
    print(f"For dataset {dataset} validation ratio is : {validated_count}/{len(data)}")
    print(
        f"-- Language mismatch count : {sum(1 for elem in data if elem['validated'] == 'Language mismatch')}"
    )
    print(
        f"-- Problematic start count : {sum(1 for elem in data if elem['validated'] == 'Problematic start')}"
    )
    print("")

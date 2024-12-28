import re
import json
import os

# Input JSONL file path
# Regex to match and replace the target pattern
pattern = r'("answer":)\s*Here[^:]*:\s*'
replacement = r"\1 "

print("Starting processing of JSONL file...\n")


def clean_summary_prefixes(answer_text):
    """
    Remove 'Here' to ':' sequence only if 'Here' appears at the start of the text.

    Args:
        answer_text (str): The text value from the answer field
    Returns:
        str: Cleaned text with prefix removed if it started with 'Here'
    """
    # Only process if the text starts with 'Here'
    if answer_text.lstrip().startswith("Here"):
        pattern = r"^\s*Here.*?:"
        cleaned_text = re.sub(pattern, "", answer_text)
        return cleaned_text.lstrip()  # Remove any leading whitespace after cleaning
    return answer_text


def process_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as infile, open(
        output_file, "w", encoding="utf-8"
    ) as outfile:
        for line_number, line in enumerate(infile, start=1):
            # Parse JSON object
            obj = json.loads(line.strip())

            if "answer" in obj:
                original_answer = obj["answer"]
                # Apply regex replacement only to the answer value
                obj["answer"] = clean_summary_prefixes(original_answer)
            else:
                print(" - No 'answer' key found in this line.")

            # Write the updated JSON object back to the output file
            outfile.write(json.dumps(obj) + "\n")


files = [
    "games_summary_fixed.jsonl",
    "metu_scrape_summary_fixed.jsonl",
    "news_summary_fixed.jsonl",
    "yeni_cnbc_sanat_summary_fixed.jsonl",
    "yeni_economist_bilim_summary_fixed.jsonl",
    "yeni_guardian_sanat_summary_fixed.jsonl",
    "yeni_sciencenews_bilim_summary_fixed.jsonl",
    "yeni_webtekno_bilim_summary_fixed.jsonl",
]
outs = [f for f in files]

file_root = "summaries_fixed"
out_root = "summaries_fixed_regex"

for file, out in zip(files, outs):
    print(f"At {file}")

    file_path = os.path.join(file_root, file)
    out_path = os.path.join(out_root, out)

    process_file(file_path, out_path)

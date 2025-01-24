import google.generativeai as genai
import os
import csv
from typing import List, IO


BATCH_SIZE = 10
OUTPUT_COLUMNS = 4

INPUT_FILE = "input_file.csv"
OUTPUT_FILE = "output_6.csv"

GEMINI_MODEL = "gemini-1.5-pro"


def generate_prompt(spanish_words: List[str]) -> str:
    """
    Generates Foreign language sentences and English translations for a batch of words.
    """
    prompt = """In the form of a csv file generate the following for the list of words provided at the end.
     'spanish_sentence', 'english_translation', 'spanish_word', 'word_definition_in_sentence'

    The sentence should contain context that will aid the reader in helping deduce the content of the word.
    If one sentences starts off with a noun and uses it as the subject use that verb as the object and do not start with it for the other sentence(s). If it is a verb
    you can vary the conjugation and pick a random tense to use like: infinitive, present, past, subjunctive, etc.

    Create up to 3 example sentences for a word. Use only 1 sentence if the word is simple and unambiguous. Use more if the word is very complex or has many different definitions all which occur with high frequency.
    Only include sentences that reflect the common uses. but do not ever exceed 4 sentences in total.

     Do not output the column headers. I simply want the results of this csv file. Each column should be wrapped in quotes.
     column_1 should be the spanish sentence. column 2 should be the translation in english. 3 should be the word used.
    4 will be the definition in english for that specific example instance -- keep this short.
     Please 
       :\n"""
    for word in spanish_words:
        prompt += f"- {word}\n"

    return prompt


class AIWrapper:

    @staticmethod
    def call_gemini(input_prompt) -> str:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(input_prompt)
        return response.text


def call_model_with_word_batch(input_words, writer: csv.writer) -> bool:
    """returns true if successfully processed.
    returns false if there was a failure"""
    prompt = generate_prompt(input_words)
    try:
        results = AIWrapper.call_gemini(prompt)
        write_to_csv(writer, results)
        return True
    except Exception as e:
        print(f"error calling google {e} -- aborting")
        return False


def write_to_csv(writer: csv.writer, response_text: str):
    reader = csv.reader(
        response_text.splitlines(),
        quotechar='"',
        delimiter=",",
        quoting=csv.QUOTE_ALL,
        skipinitialspace=True,
    )
    for row in reader:
        if not row:
            continue
        if len(row) != OUTPUT_COLUMNS:
            print(f"ERROR SKIPPING PRINTING {row} bc {OUTPUT_COLUMNS} NOT CORRECT")
        else:
            writer.writerow(row)


def process_batch(word_batch, writer):
    success = call_model_with_word_batch(word_batch, writer)
    if success:
        print(f"Processed batch")
    else:
        raise Exception("Error processing batch")


def process_word_batches(reader: csv.DictReader, writer: csv.writer):
    """
    Reads words from the input CSV reader, batches them and then processes.
    """
    word_batch = []
    batches_processed = 0

    for row in reader:
        foreign_word = row["foreign_word"]
        word_batch.append(foreign_word)

        if len(word_batch) == BATCH_SIZE:
            process_batch(word_batch, writer)
            batches_processed += 1
            word_batch = []

    # Process any remaining words
    if word_batch:
        process_batch(word_batch, writer)


def main():
    """
    Main function to handle file opening, reading, and processing.
    """
    try:
        with open(
            OUTPUT_FILE, "w", newline=""
        ) as csv_out:  # newline='' prevents extra blank rows
            writer = csv.writer(csv_out)
            with open(INPUT_FILE, "r") as input_file:
                reader = csv.DictReader(input_file)
                process_word_batches(reader, writer)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

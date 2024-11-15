import google.generativeai as genai
import os
import csv
import time
from typing import List, IO

genai.configure(api_key=os.environ["API_KEY"])


BATCH_SIZE = 10
OUTPUT_COLUMNS = 4


def generate_prompt(spanish_words: List[str]) -> str:
    """
    Generates Spanish sentences and English translations for a batch of words.
    """
    prompt = """In the form of a csv file generate the following for the list of words provided at the end.
     'spanish_sentence', 'english_translation', 'spanish_word', 'word_definition'

    What is very important is that I should be able to discern the meaning of the word based on the context. 
    Another way of saying that the sentences should be illustrative and good for a language learner.
    The above is very important that the sentence should contain a ton of context that will aid the reader in figuring out the word.
    If one sentences starts off with a noun and uses it as the subject use that verb as the object and do not start with it for the other sentence(s). If it is a verb
    you can very the conjucation and pick a random tense to use like: present, past, subjunctive, etc.


     I want you to create 2 sentences if the word is an easier word and strictly has 1 meaning without ambiguity.
     I want you to create 3 or 4 or 5 if the word is harder or it has a lot of different meanings.
     If there are multiple meanings that where more than 1 occurs frequently -- please include all relevant high frequency meanings.

     Do not output the column headers. I simply want the results of this csv file. Each column should be wrapped in quotes.
     column_1 should be the spanish sentence. column 2 should be the translation in english. 3 should be the word used. 4 will be the definition in english -- keep this short.
     Please 
       :\n"""
    for word in spanish_words:
        prompt += f"- {word}\n"

    return prompt


class AIWrapper():

    @staticmethod
    def call_gemini(input_prompt) -> str:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(input_prompt)
        return response.text



def process_batch(input_words, writer) -> bool:
    ''' returns true if successfully processed.
    returns false if there was a failure'''
    prompt = generate_prompt(input_words)
    try:
        results = AIWrapper.call_gemini(prompt)
    except Exception as e:
        print(f'error calling google {e} -- aborting')
        return False
    write_to_csv(writer, results)
    return True

    

def write_to_csv(writer,response_text: str):
    reader = csv.reader(response_text.splitlines(), quotechar='"', delimiter=',',quoting=csv.QUOTE_ALL, skipinitialspace=True)
    for row in reader:
        if not row:
            continue
        if len(row) != OUTPUT_COLUMNS:
            # raise ValueError(f'wrong output number {row}')
            print(f'ERROR SKIPPING PRINTING {row} bc {OUTPUT_COLUMNS} NOT CORRECTR')
        else:
            writer.writerow(row)



with open('output.csv', 'w') as csv_out:
    writer = csv.writer(csv_out)

    with open('spanish_diy_attempt_3.csv', 'r') as input_file:
        reader = csv.DictReader(input_file)
        word_batch = []

        batches_processed = 0
        for i, row in enumerate(reader, 1):
            if batches_processed == 3:
                break
            spanish_word = row.get('spanish_word')
            if not spanish_word:
                raise Exception('excepted word from csv')
            word_batch.append(spanish_word)
            if i % BATCH_SIZE == 0:
                if not process_batch(word_batch, writer):
                    word_batch = []
                    break
                time.sleep(2)
                batches_processed += 1 
                word_batch = []
                print(f'processed {batches_processed} results')
                

        # process left over
        if word_batch:
            process_batch(word_batch, writer)




# prompt = generate_sentences_and_translations(word_list)

# model = genai.GenerativeModel("gemini-1.5-pro")
# response = model.generate_content(prompt)
# print(response.text)




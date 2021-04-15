"""
https://github.com/onadegibert/syn-corpus-builder/blob/main/build_synthetic_corpus_conll.py
Creates a synthethic corpus in CoNLL Format
Created for Spanish, feel free to add your own gazetteers
This script expects a file in CoNLL Format and will introduce PERSON tags for tokens such as 'XXXXXX'
Author: ona.degibert@bsc.es
"""

import argparse
import os
import random
import time

class Token():
    def __init__(self, line, previous_token, previous_offset):
        self.string, self.level1, self.level2, self.onset_offset = line.split('\t')
        onset, offset = self.onset_offset.replace('(','').replace(')','').split(',')
        self.onset, self.offset = int(onset), int(offset.strip())
        self.previous_token = previous_token
        self.previous_offset = previous_offset

def parse_arguments():
    """Read command line parameters."""
    parser = argparse.ArgumentParser(description="Script to create a syntethic semi-annotated corpus")
    parser.add_argument('-d', '--directory',
                        help="Corpus directory")
    parser.add_argument('-o', '--output',
                        help="Output directory")
    args = parser.parse_args()
    return args.directory, args.output

def get_files(directory):
    files = []
    for r, d, f in os.walk(directory):
        for file in f:
            file_path = os.path.join(r, file)
            files.append([file_path, file])
    return(files)

def load_gazetteers():
    # Open files
    path = 'gazetteers'
    gazetteers = dict()
    for filename in os.listdir(path):
        with open(os.path.join(path, filename), 'r') as fn: # open in readonly mode
            gazetteers[filename.replace('.txt','')] = [token for token in fn.read().splitlines()]
    return gazetteers

def choose_gazetteers(previous_token,gazetteers):
    tokens = []
    entity_type = 'person'
    string = ''
    # m for male, f for female and s for surname
    # if it's a company we only take a surname: empresa Torras
    if previous_token.lower() in ['empresa','constructora']:
        name = ['s']
        entity_type = 'company'
    # if it's a school name we only take a name and surname: colegio Joan Torras
    elif previous_token.lower() in ['colegio','público', 'de']:
        name = random.choice([['m','s'],['f','s']])
        entity_type = 'school'
    # if the word ends in 'a', take a femenine noun
    elif previous_token[-1] == 'a':
        name = ['f','s','s']
    # if the word ends in 'o', take a masculine noun
    elif previous_token[-1] == 'o':
        name = ['m','s','s']
    # otherwise, choose randomly the gender
    else:
        name = random.choice([['m','s','s'], ['f','s','s']])
    # follow a zipf like distribution for the weights
    weights =  [5000/i for i in range(1,5001)]
    for gender in name:
        if gender == 'f':
            token = random.choices(gazetteers['female_names'], weights=weights, k=1)[0]
        if gender == 'm':
            token = random.choices(gazetteers['male_names'], weights=weights, k=1)[0]
        if gender == 's':
            token = random.choices(gazetteers['surnames'], weights=weights, k=1)[0]
        if len(token.split()) > 1: #if there's a multitoken
            for word in token.split():
                tokens.append([word, gender])
        else:
            tokens.append([token, gender])
        string = string + token + ' '
    return tokens, entity_type, string

def insert_entities(read_file, gazetteers):
    final_file = []
    previous_token = ""
    previous_offset = ""
    increased_span = 0
    mapped_tags = {'f':'given name - female','m':'given name - male','s':'family name'}
    for line in read_file:
        token = Token(line, previous_token, previous_offset)
        if token.string == 'XXXXXX':
            new_tokens, entity_type, string = choose_gazetteers(token.previous_token,gazetteers)
            bio_tag = 'B' #only first token with B tag
            first_surname = 'yes'
            for new_token, gender in new_tokens:
                token.string = new_token.capitalize()
                if entity_type == 'company' or entity_type =='school':
                        token.level1 = bio_tag+'-ORGANISATION'
                        token.level2 = 'O'
                if entity_type == 'person':
                        token.level1 = bio_tag+'-PERSON'
                        if first_surname == 'yes' and mapped_tags[gender] == 'family name': # reset biotag to B for family names
                            bio_tag = 'B'
                            first_surname = 'no'
                        token.level2 = bio_tag+'-'+mapped_tags[gender]
                token.onset = token.previous_offset + 1
                token.offset = token.onset + len(new_token)
                token.previous_offset = token.offset
                token.onset_offset = (token.onset, token.offset)
                final_file.append('\t'.join([token.string, token.level1, token.level2, str(token.onset_offset)]))
                bio_tag = 'I' # next tokens with I tag
            increased_span = increased_span + len(string) - 7 # we delete the length of XXXXXX
        else:
            token.onset = token.onset + increased_span
            token.offset = token.offset + increased_span
            token.onset_offset = (token.onset, token.offset)
            final_file.append('\t'.join([token.string, token.level1, token.level2, str(token.onset_offset)]))
        previous_token = token.string
        previous_offset = token.offset
    return final_file


def write_file(processed_file, output, filename):
    with open(os.path.join(output, filename.replace('.txt_result','_syn') ), 'w') as fn: # open in readonly mode
            for line in processed_file:
                fn.write(line+'\n')

def main(args):
    directory, output = args
    #create output folder if it doesn't exist
    if not os.path.exists(output):
            os.makedirs(output)
    files = get_files(directory)
    gazetteers = load_gazetteers()
    for file_path, filename in files:
        read_file = open(file_path, 'r')
        processed_file = insert_entities(read_file, gazetteers)
        write_file(processed_file, output, filename)

if __name__ == "__main__":
    start_time = time.time()
    args = parse_arguments()
    main(args)
    print("--- %s seconds ---" % (time.time() - start_time))
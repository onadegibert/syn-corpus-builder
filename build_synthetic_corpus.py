"""
Creates a synthethic corpus in WebAnno 3.2 TSV Format
Created for Spanish, feel free to add your own gazetteers
If there's any annotation you want to reuse, it shouldn't be punctuation!!! e.g XXXXXX
1. open file and where is ... random name + tal
Author: ona.degibert@bsc.es
"""

import argparse
import os
import re
import itertools
from annotate_token import *

def parse_arguments():
    """Read command line parameters."""
    parser = argparse.ArgumentParser(description="Script to create a syntethic semi-annotated corpus")
    parser.add_argument('-d', '--directory',
                        help="Corpus directory")
    parser.add_argument('-o', '--output',
                        help="Output directory")
    args = parser.parse_args()
    return args.directory, args.output

def read_files(path):
    # Open files
    files = []
    filenames = []
    for filename in os.listdir(path):
        filenames.append(filename)
        with open(os.path.join(path, filename), 'r') as fn: # open in readonly mode
            files.append(fn.read())
    return files, filenames

def load_gazetteers(lowercased):
    # Open files
    path = 'gazetteers'
    gazetteers = dict()
    for filename in os.listdir(path):
        with open(os.path.join(path, filename), 'r') as fn: # open in readonly mode
            if lowercased:
                one_token_gazetteers = [token.lower() for token in fn.read().splitlines() if len(token.split()) == 1]
            else:
                one_token_gazetteers = [token for token in fn.read().splitlines() if len(token.split()) == 1]
            gazetteers[filename.replace('.txt','')] = one_token_gazetteers
    return gazetteers

def convert_to_webanno(original_files, gazetteers):
    converted_files = []
    for original_file in original_files:
        converted_file = list()
        initial_text = ["#FORMAT=WebAnno TSV 3.2", "#T_SP=de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity|identifier|value",""]
        converted_file.extend(initial_text)
        sen_index = 1
        last_offset = 0
        last_tag_id = 0
        for sentence in original_file.splitlines():
            tok_index = 1
            last_tag = ""
            tokens_processed = []
            for token in re.findall(r"[\w']+|[!\"\[\]#$%&'()*+,-./:;<=>?@^_`{|}~]",sentence): #Improve sentence splitting
                sen_token_id = str(sen_index) + '-' + str(tok_index)
                onset = original_file.find(token,last_offset)
                offset = onset + len(token)
                tag_id = '_'
                tag = '_'
                if token.startswith('XX'): #List of values
                    new_token = token.replace('XX','')
                    sentence = sentence.replace(token, new_token)
                    offset = offset - 2
                    original_file = original_file.replace(token,new_token,1)
                    if new_token.lower() in gazetteers['female_names'] or new_token.lower() in gazetteers['male_names'] or new_token.lower() in gazetteers['surnames']:
                        tag_id, tag, add_tag = process_person_tag(new_token.lower(), last_tag_id, last_tag, gazetteers)
                        token = new_token
                    # Currently, we're not annotating ADDRESSES
                    #if token.lower() in gazetteers['countries'] or token.lower() in gazetteers['spanish_cities'] or token.lower() in  gazetteers['spanish_territories']:
                    #    tag_id, tag, add_tag = process_territory_tag(token.lower(), last_tag_id, last_tag, gazetteers)
                onset_offset = str(onset) + '-' + str(offset)
                tokens_processed.append('\t'.join([sen_token_id,onset_offset,token,tag_id,tag]))
                last_offset = offset
                if tag_id != '_':
                    last_tag_id += add_tag
                last_tag = tag
                tok_index += 1
            if sentence != '':
                converted_file.append("\n#Text=" + sentence)
                converted_file.extend(tokens_processed)
            sen_index += 1
        converted_files.append(converted_file)
        print("Files processed: ", len(converted_files))
    return converted_files

def write_files(annotated_files,output, filenames, format):
    index = 0
    for annotated_file in annotated_files:
        with open(os.path.join(output, filenames[index].replace('txt',format)), 'w') as fn: # open in readonly mode
            for line in annotated_file:
                fn.write(line+'\n')
            index += 1


def main():
    directory, output = parse_arguments()
    files, filenames = read_files(directory)
    gazetteers = load_gazetteers(lowercased="True")
    converted_files = convert_to_webanno(files, gazetteers)
    #Afegir anotacions etc
    write_files(converted_files, output, filenames, 'tsv')

if __name__ == "__main__":
        main()
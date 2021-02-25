"""
Created for Spanish, feel free to add your own gazetteers
Insert one token names and surnames where XXXXXX
Author: ona.degibert@bsc.es
"""

from build_synthetic_corpus import *
import random

def choose_gazetteers(previous_token,gazetteers):
    token = ""
    # m for male, f for female and s for surname
    possible_male_names = [['m'],['m','s']] 
    possible_female_names = [['f'],['f','s']]
    all_possible = possible_female_names + possible_male_names
    if previous_token[-1] == 'a':
        name = random.choice(possible_female_names)
    elif previous_token[-1] == 'o':
        name = random.choice(possible_male_names)
    else:
        name = random.choice(all_possible)
    print(name)
    for name_category in name:
        if name_category == 'f':
            token = 'XX' + random.choice(gazetteers['female_names'])
        if name_category == 'm':
            token = 'XX' + random.choice(gazetteers['male_names'])
        if name_category == 's':
            token = token + ' XX' + random.choice(gazetteers['surnames'])
    return token


def substitute_gazetteers(files, gazetteers):
    synthetic_files = []
    for file in files:
        new_file = []
        for sentence in file.split('\n'):
            new_sentence = []
            previous_token = ""
            for token in sentence.split():
                if token == 'XXXXX':
                    token = choose_gazetteers(previous_token, gazetteers)
                new_sentence.append(token)
                previous_token = token
            new_sentence_str = ' '.join(new_sentence)
            new_file.append(new_sentence_str.replace(' ,',',').replace(' .','.'))
        synthetic_files.append(new_file)
    return synthetic_files

def main():
    directory, output = parse_arguments()
    files, filenames = read_files(directory)
    gazetteers = load_gazetteers(False)
    synthetic_files = substitute_gazetteers(files,gazetteers)
    write_files(synthetic_files, output, filenames, 'txt')

if __name__ == "__main__":
        main()
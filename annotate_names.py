"""
Creates a synthethic corpus in WebAnno TSV v3.2 Format
Created for Spanish, feel free to add your own gazetteers
It expects pre-annotated files in  WebAnno TSV v3.2 Format with some pre-annotations.
It inserts name + surname + surname where there are XXXXX in the text.
Author: ona.degibert@bsc.es
"""

import argparse
import os
import re
import itertools
from annotate_token import *
from insert_gazetteers import *

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

def choose_gazetteers(previous_token,gazetteers):
    token = ""
    # m for male, f for female and s for surname
    possible_male_names = [['m','s','s']] 
    possible_female_names = [['f','s','s']]
    all_possible = possible_female_names + possible_male_names
    if previous_token.lower() in ['empresa','constructora']:
        name = ['s']
    elif previous_token.lower() in ['colegio','público']:
        name = random.choice([['m','s'],['f','s']])
    elif previous_token[-1] == 'a':
        name = random.choice(possible_female_names)
    elif previous_token[-1] == 'o':
        name = random.choice(possible_male_names)
    else:
        name = random.choice(all_possible)
    for name_category in name:
        if name_category == 'f':
            token = random.choice(gazetteers['female_names'][:500])
        if name_category == 'm':
            token = random.choice(gazetteers['male_names'][:500])
        if name_category == 's':
            token = token + ' ' + random.choice(gazetteers['surnames'][:500])
    return token.split(), name

def add_person_annotations(original_files, gazetteers):
    # add person tags
    annotated_files = []
    mapped_tags = {'f':'given name - female','m':'given name - male','s':'family name'}
    for original_file in original_files:
        all_used_names = []
        sentences = original_file.splitlines()
        annotated_file = sentences[0:4]
        annotation_count = 1
        for line in sentences[4:]:
            tokens_processed = []
            if line != ''  and line[0].isdigit():
                sen_token_id, onset_offset, token, tag_id_str, tag, empty_string = line.split('\t')
                if token == 'XXXXX':
                    tokens, tags = choose_gazetteers(previous_token, gazetteers)
                    all_used_names.append(tokens)
                    count = 0
                    for token in tokens:
                        if tags[count] == "s" and count == 0:
                            tag_id_str = "*"
                            tag = "ORGANISATION"
                            tokens_processed.append('\t'.join([sen_token_id,onset_offset,token,tag_id_str,tag,'']))
                        else:
                            tag_id_str = "*[" + str(annotation_count) + "]|*["+ str(annotation_count) + "]"
                            tag = "PERSON[" + str(annotation_count) + "]|" + mapped_tags[tags[count]] + "["+ str(annotation_count) + "]"
                            tokens_processed.append('\t'.join([sen_token_id,onset_offset,token,tag_id_str,tag,'']))
                        count += 1
                    annotated_file.extend(tokens_processed)
                    annotation_count += 1
                else:
                    if token == 'de' and 'DATE' in tag:
                        tag_id_str = tag_id_str.split("|")[0]
                        tag = tag.split("|")[0]
                        line = '\t'.join([sen_token_id,onset_offset,token,tag_id_str,tag,''])
                    annotated_file.append(line)
                previous_token = token
            else:
                annotated_file.append(line)
        # Replace XXXXX in text
        annotated_file_str = '|||'.join(annotated_file)
        for each_name in all_used_names:
            annotated_file_str = annotated_file_str.replace('XXXXX',' '.join(each_name), 1)
        annotated_files.append(annotated_file_str.split('|||'))
        print("Files processed: ", len(annotated_files))
    return annotated_files

def fix_onset_offset(annotated_files):
    # fix onset_offsets
    fixed_files = []
    for annotated_file in annotated_files:
        fixed_file = annotated_file[0:5]
        string_file = ' '.join(re.findall('#Text=.*\n','\n'.join(annotated_file))).replace('#Text=','')
        last_offset = 0
        previous_token = '"'
        for line in annotated_file[5:]:
            tokens_processed = []
            if line != ''  and line[0].isdigit():
                sen_token_id, onset_offset, token, tag_id_str, tag, empty_string = line.split('\t')
                onset, offset = onset_offset.split('-')
                onset = string_file.find(token)
                replace_string = 'X'*len(token)
                string_file = string_file.replace(token,replace_string,1)
                offset = onset + len(token)
                onset_offset = '-'.join([str(onset),str(offset)])
                tokens_processed.append('\t'.join([sen_token_id,onset_offset,token,tag_id_str,tag]))
                fixed_file.extend(tokens_processed)
                last_offset = offset
                previous_token = token
            elif line.startswith('#'):
                fixed_file.append(line)
                last_offset += 1
                previous_token = '.'
            else:
                fixed_file.append(line)
        fixed_files.append(fixed_file)
    return(fixed_files)

def fix_annotation_counts(fixed_files):
    # fix annotation counts
    final_files = []
    for fixed_file in fixed_files:
        index_person = [idx for idx, s in enumerate(fixed_file) if 'PERSON' in s][0]
        final_file = fixed_file[0:index_person]
        re_tags_number_tag = re.compile('\*\[\d+\]')
        all_used_tag_ids = re_tags_number_tag.findall(' '.join(final_file))
        if not all_used_tag_ids:
            last_tag_id = 0
        else:
            used_tag_ids_int = [int(id) for id in re.findall('\d+',' '.join(all_used_tag_ids))]
            last_tag_id = max(used_tag_ids_int)
        last_tag_id = int(last_tag_id)
        last_name_level_1 = ''
        last_name_level_2 = ''
        increased_tag_count = 0
        for line in fixed_file[index_person:]:
            tokens_processed = []
            if line != ''  and line[0].isdigit(): # If it's an annotation
                sen_token_id, onset_offset, token, tag_id_str, tag = line.split('\t')
                if tag_id_str != "_" and tag_id_str != '*':
                    re_tags_number = re.compile('\d+')
                    re_tags_name = re.compile('[a-zA-Z -]+')
                    if len(tag.split("|")) > 1: # there are two tags
                        tag_level_1, tag_level_2 = re_tags_number.findall(tag_id_str)
                        tag_name_level_1, tag_name_level_2 = re_tags_name.findall(tag)
                        tag_level_1 = int(tag_level_1)
                        tag_level_2 = int(tag_level_2)
                        # PERSON ENTITITES
                        if tag_name_level_2 == 'family name': #means it's a person annotation
                            if last_name_level_2 == 'family name': # second surname
                                tag_level_1 = last_tag_id - 2
                                tag_level_2 = last_tag_id
                            else:
                                tag_level_1 = last_tag_id - 1
                                tag_level_2 = last_tag_id + 1
                            increased_tag_count += 1
                        elif tag_name_level_2.startswith('given name'):
                            tag_level_1 = last_tag_id + 1
                            tag_level_2 = last_tag_id + 2
                            increased_tag_count += 2
                        else:
                        # OTHER ENTITIES
                            tag_level_1 = tag_level_1 + increased_tag_count
                            tag_level_2 = tag_level_2 + increased_tag_count
                        tag_id_str = "*[" + str(tag_level_1) + "]|*["+ str(tag_level_2) + "]"
                        tag_id = tag_level_2
                        tag = re.sub('(\d+)', str(tag_level_1), tag, 1)
                        tag = tag.split("|")[0]+'|'+re.sub('(\d+)', str(tag_level_2), tag.split("|")[1])
                    else:
                        tag_level_1_list = re_tags_number.findall(tag_id_str)
                        tag_level_1 = int(tag_level_1_list[0]) + increased_tag_count
                        tag_name_level_1 = re_tags_name.findall(tag)
                        tag_id_str = "*[" + str(tag_level_1) + "]"
                        tag = re.sub('\d+', str(tag_level_1), tag)
                        tag_level_2 = tag_level_1
                    last_tag_id = tag_level_2
                    last_name_level_1 = tag_name_level_1
                    last_name_level_2 = tag_name_level_2
                final_file.extend(['\t'.join([sen_token_id,onset_offset,token,tag_id_str,tag])])
            else:
                final_file.append(line)
        final_files.append(final_file)
    return(final_files)

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
    gazetteers = load_gazetteers(lowercased=False)
    annotated_files = add_person_annotations(files, gazetteers)
    fixed_files = fix_onset_offset(annotated_files)
    final_files = fix_annotation_counts(fixed_files)
    #Afegir anotacions etc
    write_files(final_files, output, filenames, 'tsv')

if __name__ == "__main__":
        main()
"""
Given a list of male and female names, creates 10k random names composed of:
name + first name + second name

It expects a folder called 'gazeteers' with three files within it:
- female_names.txt
- male_names.txt
- surnames.txt
Author: ona.degibert@bsc.es
"""
import random
import os
from collections import Counter

def load_gazetteers():
    # Open files
    path = 'gazetteers'
    gazetteers = dict()
    for filename in os.listdir(path):
        with open(os.path.join(path, filename), 'r') as fn: # open in readonly mode
            gazetteers_list = fn.read().splitlines()
            gazetteers[filename.replace('.txt','')] = gazetteers_list
    return gazetteers

def random_zipf(list):
    # follow a zipf like distribution for the weights
    weights =  [5000/i for i in range(1,5001)]
    return random.choices(list, weights=weights, k=5000)

def create_names(gazetteers):
    male_names = random_zipf(gazetteers['male_names'])
    female_names = random_zipf(gazetteers['female_names'])
    names = male_names + female_names
    first_surnames_m = random_zipf(gazetteers['surnames'])
    second_surnames_m = random_zipf(gazetteers['surnames'])
    first_surnames_f = random_zipf(gazetteers['surnames'])
    second_surnames_f = random_zipf(gazetteers['surnames'])
    random_names_m = zip(male_names, first_surnames_m, second_surnames_m)
    random_names_f = zip(female_names, first_surnames_f, second_surnames_f)
    random_names_list = [' '.join(name) for name in random_names_m] + [' '.join(name) for name in random_names_f]
    # això genera noms repetits l'ideal seria no repetir noms. Potser generar llista zipf de noms i després afegir cognoms si no existeix ja a la llistA?
    return sorted(random_names_list)

def print_stats(names):
    names_len = [len(name.split()) for name in names]
    counts = Counter(names_len)
    total = sum(counts.values())
    print('\t'.join(['LEN','COUNT','%']))
    for each_len in sorted(counts):
        print('\t'.join([str(each_len),str(counts[each_len]),str(counts[each_len]*100/total)]))

def write_files(list):
    with open('10k_random_names_zipf_repetition.txt', 'w') as fn: 
        for line in list:
            fn.write(line+'\n')

def main():
    gazetteers = load_gazetteers()
    random_names = create_names(gazetteers)
    print_stats(random_names)
    write_files(random_names)
    
if __name__ == "__main__":
        main()
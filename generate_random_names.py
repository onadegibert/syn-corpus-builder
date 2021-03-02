"""
Given a list of male and female names, creates 10k random names composed of:
name + first name + second name
Author: ona.degibert@bsc.es
"""

from insert_gazetteers import *

def create_names(gazetteers):
    random_names = []
    all_names = gazetteers['female_names']+gazetteers['male_names']
    surnames = gazetteers['surnames']
    surnames_counts = [(surname,0) for surname in surnames]
    count = 0
    for name in all_names:
        surnames = []
        for each_surname in range(2): # we need to generate two surnames
            # get all counts
            counts = [surname_tuple[1] for surname_tuple in surnames_counts if surname_tuple[1] == count]
            # check if there's still some available, otherwise, increase count
            if count not in counts:
                count += 1
            # select only surnames with the correspondent count
            available_surnames = [surname_tuple[0] for surname_tuple in surnames_counts if surname_tuple[1] == count]
            # choose one randomly and increase count
            name_surname = random.choice(available_surnames)
            index = surnames_counts.index((name_surname,count))
            surnames_counts[index] = (name_surname,count+1)
            surnames.append(name_surname)
        random_name = ' '.join([name] + surnames)
        random_names.append(random_name)
    return random_names

def write_files(list):
    with open('10k_random_names.txt', 'w') as fn: 
        for line in list:
            fn.write(line+'\n')

def main():
    #gazetteers = load_gazetteers(lowercased=False)
    gazetteers = {'female_names': ['Ona','Laura','Dafne'], 'male_names': ['Joan','Bernat','Lluís'], 'surnames': ['Sánchez','García','Oró', 'Lima']}
    random_names = create_names(gazetteers)
    print(random_names)
    write_files(random_names)
    
if __name__ == "__main__":
        main()
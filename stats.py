from collections import Counter

def main():
    f = open('10k_random_names.txt')
    names = f.read().splitlines()
    names_len = [len(name.split()) for name in names]
    counts = Counter(names_len)
    total = sum(counts.values())
    for each_len in counts:
        print('\t'.join([str(each_len),str(counts[each_len]),str(counts[each_len]*100/total)]))


if __name__ == "__main__":
        main()
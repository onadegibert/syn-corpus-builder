#!/bin/bash
# Runs the whole pipeline

# 1. Convert ...... placeholders to XXXXXX
# sed -i 's/\.\.\.\.\.\./XXXXX/g' dir/*

# 2. Remove spaces at the beggining of the sentences
# sed -i s'/^ //' dir/*

# 3. Insert gazetteers
python3 insert_gazetteers.py -d 1_testset/ -o 2_testset_syn/

# 4. Convert to anno format
python3 build_synthetic_corpus.py -d 2_testset_syn/ -o 3_testset_syn_tsv/
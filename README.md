# syn-corpus-builder
It is aimed at Spanish and automatic insertion of proper nouns.

## Usage
It expects files where placeholders for nouns are XXXXX.
There are two mains scripts meant to be run one after the other
```sh
python3 insert_gazetteers.py -d data_dir/ -o output_dir/
python3 build_synthetic_corpus.py -d data_dir/ -o output_dir/
```
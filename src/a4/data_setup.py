from urllib.request import urlretrieve
from os import remove, mkdir, path
from zipfile import ZipFile
from db import DATA_PATH

def run():
    if path.exists(DATA_PATH):
        print('data path already exists')
        return

    urlretrieve('https://dbresearch.uni-salzburg.at/downloads/teaching/2019ss/dbt/dblp.zip', 'dblp.zip')
    mkdir(DATA_PATH)
    f = ZipFile('dblp.zip', 'r')
    f.extractall(DATA_PATH)
    f.close()
    remove('dblp.zip')

if __name__ == "__main__":
    run()

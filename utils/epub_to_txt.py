
# Import required modules for merging files
import glob
import shutil
import os.path

path_folder='./'

import ebooklib
from ebooklib import epub


def epub2thtml(epub_path):
    book = epub.read_epub(epub_path)
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    return chapters


for filename in glob.glob(path_folder+'*.epub'):
    print(filename)
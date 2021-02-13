
# Import required modules for merging files
import glob
import shutil
import os, fnmatch
import os.path
import pdftotext
import ebooklib
from ebooklib import epub

data_folder='../../Google Drive/data/' #Update path where data is if needed
merged_txt_path='./data/all_txt_1302.txt'#Update Path and Name merged data.

#####------------PRELIMINARIES
def findfiles (path, filter):
    for root, dirs, files in os.walk(path):
        for file in fnmatch.filter(files, filter):
            yield os.path.join(root, file)
            

#####------------CONVERSION PDF to TXT
#for filename in glob.glob(data_folder+'*.pdf'): OLD WAY

def pdftotxt():
    print("Start conversion pdf to txt of the pdf.")
    for pdffile in findfiles(data_folder, '*.pdf'):#CATCH ALL txt
        filename = os.path.basename(pdffile)
        print(filename)
        with open(pdffile, "rb") as f:
            pdf = pdftotext.PDF(f)
        txtfile=pdffile.replace(".pdf",".txt")
        print("Converting to txt:"+txtfile)
        with open(txtfile, 'w') as f:
            f.write("\n\n".join(pdf))
    print("Converted all pdf to txt.")
#pdftotxt()

#####------------CONVERSION ALL EPUB to TXT
def epub2thtml(epub_path):
    book = epub.read_epub(epub_path)
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    return chapters


def epubtotxt():
    print("Start conversion epub to txt.")
    for epubfile in findfiles(data_folder, '*.epub'):
        filename = os.path.basename(epubfile)
        print(filename)
        chapters=epub2thtml(epubfile)
        print(chapters)
        txtfile=epubfile.replace(".epub",".txt")
        print("Converting to txt:"+txtfile)
        with open(txtfile, 'w') as f:
            f.write("\n\n".join(chapters))
    print("Converted all epub to txt.")

#epubtotxt()#ISSUE currently

#####------------CONVERSION ALL DJVU to TXT

def djvutotxt():
    print("Start conversion djvu to txt.")
    for djvufile in findfiles(data_folder, '*.djvu'):
        filename = os.path.basename(epubfile)
        print(filename)
        txtfile=epubfile.replace(".epub",".txt")
        print("Converting to txt:"+txtfile)
        pass

#####----------MERGE TXT into newfile

def mergetxt():
    print("Start merging")
    #Combine your uploaded files into one called merged.txt
    with open(merged_txt_path, 'a+') as outfile:
        for filename in glob.glob(data_folder+'*.txt'):
            with open(filename, 'r') as readfile:
                print("starting the file"+filename)
                shutil.copyfileobj(readfile, outfile)
                print("Added the txt file"+filename)
        print(f'merged Text created in {data_folder}data/')
#mergetxt()

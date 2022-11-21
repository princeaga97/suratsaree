from PIL import Image
import os, sys
import pathlib


path = "/home/princej/suratsaree/media/"
dirs = os.listdir( path )
def resize():
    for item in dirs:
        print(item)
        if os.path.isfile(path+item):
            im = Image.open(path+item)
            f, e = os.path.splitext(path+item)
            print(f,e)
            basewidth = 800
            wpercent = (basewidth / float(im.size[0]))
            hsize = int((float(im.size[1]) * float(wpercent)))
            im = im.resize((basewidth, hsize), Image.ANTIALIAS)
            im.save(path+item)
resize()
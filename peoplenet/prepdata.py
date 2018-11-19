import csv
import random
import os
import cv2
import numpy as np
from config import *
from scipy.misc import imread,imsave
from PIL import Image
import sys

datasetdir = "dataset/"
def umdcsvtobb(datafile):
        tagfile = os.path.join(os.path.dirname(datafile),os.path.basename(datafile).split(".")[0]+".txt")
        boxes = []
        imsize = 608
        with open(tagfile) as fh:
                box = fh.read().strip('\n').split(" ")
                ret = {
                        "id":0,
                        "filename":"",
                        "xpos":0,
                        "ypos":0,
                        "w":0,
                        "h":0
                }
                ret["id"] = int(box[0])
                ret["filename"] = datafile
                ret["xpos"] = float(box[1])*imsize
                ret["ypos"] = float(box[2])*imsize
                ret["w"] = float(box[3])*imsize
                ret["h"] = float(box[4][:-3])*imsize
                boxes.append(ret)
        return boxes

def randombb(imagesize):
        ret = {
                "id":0,
                "filename":"",
                "xpos":0,
                "ypos":0,
                "w":0,
                "h":0
              }
        ret["id"] = -1
        ret["filename"] = "NULL"
        print imagesize
        ret["xpos"] = random.uniform(40,imagesize[0]-80)
        ret["ypos"] = random.uniform(40,imagesize[1]-80)
        ret["w"] = 80
        ret["h"] = 80
        return ret

def displaybb(boundbox):
        image = cv2.imread(os.path.join(datasetdir,"umdfaces_batch1",boundbox["filename"]))
        if not image:
                print("image not found")
                return
        cv2.imshow(image)
        cv2.waitKey(30)

def preppeople(datadir, trainvalidratio=10):
        traindir = datadir + "train/"
        validdir = datadir + "valid/"
        datafile = "mlemtrain.txt"
        data = []
        with open(datafile, 'r') as fh:
                for line in fh:
                        data.append(line.strip('\n'))
        lengthofdata = len(data)
        ids = 0
        pad = 80
        for dfile in data:
                boxes = umdcsvtobb(dfile)
                for box in boxes:
                        img = imread(box['filename'])
                        padimg = np.ones((img.shape[0]+pad,img.shape[1]+pad,img.shape[2]))*255
                        padimg[pad/2:-pad/2,pad/2:-pad/2,:] = img
                        area = (int(round(box['xpos']-box['w']/2)),
                                int(round(box['ypos']-box['h']/2)), 
                                int(round(box['xpos']+box['w']/2)),
                                int(round(box['ypos']+box['h']/2)))

                        print box
                        boximg = padimg[area[1]+pad/2:area[3]+pad/2,area[0]+pad/2:area[2]+pad/2,:]
                        if ids%trainvalidratio == 0:
                                box['filename'] = os.path.join(validdir,"person","{}.jpg".format(ids))
                        else:
                                box['filename'] = os.path.join(traindir,"person","{}.jpg".format(ids))
                        try:
                                imsave(box['filename'],boximg)
                        except Exception as e:
                                print e
                                print img.shape, area
                                cv2.imshow("box",img[area[1]:area[3],0:area[2],:])
                                cv2.waitKey(0)
                                sys.exit(0)
                        ids += 1
                        boximg = np.rot90(boximg)
                        if ids%trainvalidratio == 0:
                                box['filename'] = os.path.join(validdir,"person","{}.jpg".format(ids))
                        else:
                                box['filename'] = os.path.join(traindir,"person","{}.jpg".format(ids))
                        imsave(box['filename'],boximg)
                        ids += 1
                        boximg = np.rot90(boximg)
                        if ids%trainvalidratio == 0:
                                box['filename'] = os.path.join(validdir,"person","{}.jpg".format(ids))
                        else:
                                box['filename'] = os.path.join(traindir,"person","{}.jpg".format(ids))
                        imsave(box['filename'],boximg)
                        ids += 1
                        boximg = np.rot90(boximg)
                        if ids%trainvalidratio == 0:
                                box['filename'] = os.path.join(validdir,"person","{}.jpg".format(ids))
                        else:
                                box['filename'] = os.path.join(traindir,"person","{}.jpg".format(ids))
                        imsave(box['filename'],boximg)
                        ids += 1
                        print("person",box)

def prepback(datadir, numback,trainvalidratio=10):
        backgroundfeeddir = datasetdir + "background/"
        traindir = datadir + "train/"
        validdir = datadir + "valid/"
        bkgroundimgs = os.listdir(backgroundfeeddir)
        picnum = 20000
        for i in range(numback):
                backimg = bkgroundimgs[picnum%len(bkgroundimgs)]
                img = imread(os.path.join(backgroundfeeddir,backimg))
                box = randombb(img.shape)
                box['id'] = picnum
                box['filename'] = os.path.join(backgroundfeeddir,backimg)
                area = (int(box['xpos']-box['w']/2),
                        int(box['ypos']-box['h']/2), 
                        int(box['xpos']+box['w']/2),
                        int(box['ypos']+box['h']/2))
                boximg = img[area[0]:area[2],area[1]:area[3],:]
                if box['id']%trainvalidratio == 0:
                        box['filename'] = os.path.join(validdir,"notperson","{}.jpg".format(box['id']))
                else:
                        box['filename'] = os.path.join(traindir,"notperson","{}.jpg".format(box['id']))

                print area
                imsave(box['filename'],boximg)
                print("notperson",box)
                picnum += 1
                
if __name__ == "__main__":
        preppeople("data/densedetectpeep", trainvalidratio=11)
        #prepback("data/densedetectpeep", 10000,trainvalidratio=11)

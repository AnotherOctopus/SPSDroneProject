from keras.models import load_model
from PIL import Image
import numpy as np
import cv2
from scipy.misc import imread, imsave
from skimage.transform import pyramid_gaussian
from detectpeoplemodel import detectpeep
from config import *
import os

STEP = 10
MAXCONF = 65536
font = cv2.FONT_HERSHEY_SIMPLEX
IOUTHRESH = 0.05
propsectdir = "/home/cephalopodoverlord/DroneProject/SPSDroneProject/taggingserver/dynamictrain/prospective/"
framedir = "/home/cephalopodoverlord/DroneProject/SPSDroneProject/peoplenet/dataset/rawsetframes/rawset2_stable"
outframedir = "out"
prospectid = 0
# returns a compiled model
# identical to the previous one
def runframe(model,frame,wsize):
        maxX = frame.shape[1]
        maxY = frame.shape[2]
        data = np.zeros((int((maxX-wsize)/STEP) + 1,int((maxY-wsize)/STEP) + 1))
        framebuffer = np.zeros((data.shape[0],wsize,wsize,3))
        yistep = data.shape[0]
        for yi,y in enumerate(range(0,maxY - wsize + 1,STEP)):
                for xi,x in enumerate(range(0,maxX - wsize + 1,STEP)):
                        lowwindx = x
                        lowwindy = y
                        maxwindx = x + wsize
                        maxwindy = y + wsize
                        framebuffer[xi,:,:,:] = frame[:,lowwindx:maxwindx,lowwindy:maxwindy,:]
                data[:, yi] = model.predict(framebuffer)[:,0]
                print "{} percent run".format(float(yi)/data.shape[1]*100)
        return data
#2282
def NMS(boxes):
        numboxesremoved = 0
        idx = 0
        print boxes.shape
        while idx < len(boxes) -1 :
                if boxes[idx][0] == MAXCONF:
                        idx += 1
                        continue
                def IOU(boxA):
                        if boxA[0] == MAXCONF:
                                return 0 
                        boxA =  boxA[1:]
                        boxB =  boxes[idx][1:]
                        aX1 = int(boxA[0])
                        aX2 = int(boxA[2])
                        aY1 = int(boxA[1])
                        aY2 = int(boxA[3])
                        bX1 = int(boxB[0])
                        bX2 = int(boxB[2])
                        bY1 = int(boxB[1])
                        bY2 = int(boxB[3])
                        boxAArea = (aX2 - aX1 ) * (aY2 - aY1)
                        boxBArea = (bX2 - bX1 ) * (bY2 - bY1)

                        x_over = max(0,min(aX2,bX2) - max(aX1,bX1))
                        y_over = max(0,min(aY2,bY2) - max(aY1,bY1))
                        interArea = x_over*y_over
                
                        # compute the area of both the prediction and ground-truth
                        # rectangles
                        union = float(boxAArea + boxBArea - interArea)
                        if union == 0:
                                return 0 
                
                        # compute the intersection over union by taking the intersection
                        # area and dividing it by the sum of prediction + ground-truth
                        # areas - the interesection area
                        iou = interArea / union
                        # return the intersection over union value
                        return iou

                ious = np.apply_along_axis(IOU,1,boxes[idx+1:,:])
                for iouidx, iou in enumerate(ious):
                        if iou > IOUTHRESH:
                                boxes[idx+iouidx+1] = np.asarray([MAXCONF,0,0,0,0])
                                numboxesremoved += 1
                idx += 1
                boxes  = boxes[boxes[:,0].argsort()]
        if numboxesremoved == 0:
                return boxes
        return boxes[:-numboxesremoved]
if __name__ == "__main__":
        model = load_model('netpeep.h5')
        imgcnt = 0
        for frame in os.listdir(framedir):
                testfile = os.path.join(framedir,frame)
                rawimg = imread(testfile,mode='RGB')
                X = rawimg.shape[0]
                Y = rawimg.shape[1]
                frame = rawimg.astype(np.float32)/255
                frame = frame[np.newaxis,:]
                confidence =  runframe(model,frame,80)
                imageatscale = rawimg.copy()

                bbwi = 80
                confToPos = lambda x: (x*STEP)

                threshedboxes = (confidence > 0.90 ).nonzero()
                boxes = np.zeros((len(threshedboxes[0]),5))
                for i, box in enumerate(threshedboxes[0]):
                        xidx = threshedboxes[1][i]
                        yidx = threshedboxes[0][i]
                        X = confToPos(xidx)
                        Y = confToPos(yidx)
                        boxes[i,:] = np.array([MAXCONF*(1-confidence[yidx][xidx]),X,Y,X+bbwi,Y+bbwi])
                boxes  = boxes[boxes[:,0].argsort()]
                boxes = NMS(boxes)

                for box in boxes:
                        cv2.putText(imageatscale,str(int(box[0])),(int(box[1]),int(box[2])), font, 1,(0,0,0),2,cv2.LINE_AA)
                        imageatscale = cv2.rectangle(imageatscale,(int(box[1]),int(box[2])),(int(box[3]),int(box[4])),(255,0,0))
                cv2.imwrite("out/out{}.png".format(str(imgcnt).zfill(4)),imageatscale)
                imgcnt += 1

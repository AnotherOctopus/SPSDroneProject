import os
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras import backend as K
from keras.utils import np_utils,to_categorical
from scipy.misc import imread, imsave, imresize
from sklearn.preprocessing import LabelEncoder
from detectpeoplemodel import detectpeep
from config import *
import numpy as np
from keras.models import load_model

def trainnetpeep():

    # dimensions of images
    img_width, img_height = L1Size,L1Size
    # data
    train_data_dir = "data/train"
    validation_data_dir = "data/valid"
    nb_train_samples = len(os.listdir(train_data_dir +"/person")) + len(os.listdir(train_data_dir +"/notperson"))
    nb_validation_samples = len(os.listdir(validation_data_dir +"/notperson")) + len(os.listdir(validation_data_dir +"/notperson"))
    print nb_train_samples
    n_epochs = 20
    batch_size = 128

    if K.image_data_format() == 'channels_first':
        input_shape = (3, img_width, img_height)
    else:
        input_shape = (img_width, img_height, 3)


    ## build model
    d12 = detectpeep()
    d12.compile()
    model = d12.model


    # data augmentation
    train_datagen = ImageDataGenerator(rescale=1. / 255,
                                       horizontal_flip=True,
                                       vertical_flip=True)
    test_datagen = ImageDataGenerator(rescale=1. / 255)

    train_generator = train_datagen.flow_from_directory(train_data_dir,
                                                        target_size=(img_width, img_height),
                                                        batch_size=batch_size,
                                                        class_mode='binary')
    validation_generator = test_datagen.flow_from_directory(validation_data_dir,
                                                            target_size=(img_width, img_height),
                                                            batch_size=batch_size,
                                                            class_mode='binary')

    print model.summary()
    # Train
    model.fit_generator(train_generator,
                        steps_per_epoch=nb_train_samples // batch_size,
                        epochs=n_epochs,
                        validation_data=validation_generator,
                        validation_steps=nb_validation_samples // batch_size,
                        shuffle=True,
                        verbose=1)

    model.save("netpeep.h5")

if __name__ == "__main__":
    trainnetpeep()
    testfile = "/home/cephalopodoverlord/DroneProject/SPSDroneProject/peoplenet/data/train/person/2.jpg"
    model = load_model('netpeep.h5')
    rawimg = imread(testfile,mode='RGB').astype(np.float32)/255
    rawimg = rawimg[np.newaxis,...]
    predictions =  model.predict(rawimg)
    print predictions

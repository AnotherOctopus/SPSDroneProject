from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential,Model
from keras.layers import Conv2D, MaxPooling2D, Reshape
from keras.layers import Activation, Dropout, Flatten, Dense,Input
from keras.optimizers import Adam, SGD
from keras import backend as K
import numpy as np

class detectpeep(object):
        def __init__(self):
                ## build model
                inp = Input(shape=(80,80,3),dtype='float32')
                x = Conv2D(64, (12, 12), strides = 2,padding="same")(inp)
                x = Activation("relu")(x)
                x = Conv2D(64, (3, 3), strides = 1,padding="same")(x)
                x = Activation("relu")(x)
                x = MaxPooling2D(pool_size=(3,3),strides=2)(x)
                x = Flatten()(x)
                x = Dense(32)(x)
                x = Activation("relu")(x)
                x = Dense(1)(x)
                x = Activation("sigmoid")(x)
                self.model = Model(inputs=inp,outputs=x)
                self.inp = inp
                self.out = x
        def compile(self):

                self.model.compile(loss='binary_crossentropy',
                          optimizer='adam',
                          metrics=['accuracy'])


class deepdetectpeep(object):
        def __init__(self):
                ## build model
                inp = Input(shape=(80,80,3),dtype='float32')
                x = Conv2D(128, (12, 12), strides = 2,padding="same")(inp)
                x = Activation("relu")(x)
                x = Conv2D(64, (6, 6), strides = 1,padding="same")(x)
                x = Activation("relu")(x)
                x = Conv2D(64, (3, 3), strides = 1,padding="same")(x)
                x = Activation("relu")(x)
                x = MaxPooling2D(pool_size=(3,3),strides=2)(x)
                x = Flatten()(x)
                x = Dense(128)(x)
                x = Activation("relu")(x)
                x = Dense(64)(x)
                x = Activation("relu")(x)
                x = Dense(1)(x)
                x = Activation("sigmoid")(x)
                self.model = Model(inputs=inp,outputs=x)
                self.inp = inp
                self.out = x
        def compile(self):

                self.model.compile(loss='binary_crossentropy',
                          optimizer='adam',
                          metrics=['accuracy'])


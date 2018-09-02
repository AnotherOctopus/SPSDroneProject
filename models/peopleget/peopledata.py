import numpy as np
from pickle import dumps, loads
import zlib
from scipy.spatial import distance


class PeopleData(object):
    def __init__(self, deltat = 0.05):
        self.dt = deltat
        self.people = []

    def append(self, val):
        if type(val) != PersonData:
            raise TypeError("CAN ONLY APPEND PEOPLE")
        self.people.append(val)

    def __str__(self):
        return "Number of People {}".format(len(self.people))

    def stateS(self,stepnum):
        if type(stepnum) != int:
            raise TypeError("STEPNUM MUST BE AN INTEGER")
        return [(p.ID, p.xpos[stepnum], p.ypos[stepnum], p.dx[stepnum], p.dy[stepnum]) for p in self.people]

    def stateT(self, time):
        return self.stateS(int(time/self.dt))


class PersonData(object):
    def __init__(self, IDnum,
                 ypositions=np.zeros(1000, dtype=float),
                 xpositions =np.zeros(1000, dtype=float),
                 xvelocities=np.zeros(1000, dtype=float),
                 yvelocities =np.zeros(1000, dtype=float)):
        self.ID = IDnum
        if len(set([len(ypositions), len(xpositions), len(yvelocities), len(xvelocities)])) != 1:
            raise ValueError("ALL STATE LISTS MUST BE THE SAME LENGTH")

        self.numdata = len(ypositions)

        if any(type(arg) != np.ndarray for arg in [ypositions, xpositions, ypositions, xvelocities]):
            raise TypeError("ALL INPUTS NEED TO BE NUMPY ARRAYS")

        self.ypos = ypositions
        self.xpos = xpositions
        self.dy = yvelocities
        self.dx = xvelocities

    def getDest(self):
        raise Exception("IMPLEMENT THE GET DESDT FUNCTION IN YOUR MODEL")


class Person(object):
    def __init__(self, pos=np.array((0, 0)),
                       vel=np.array((0, 0)),
                       dest=np.array((0, 0)),
                       orient=0.0):
        if pos.shape != (2,):
            raise ValueError("POS NOT CORRECT SHAPE", pos.shape)
        if vel.shape != (2,):
            raise ValueError("POS NOT CORRECT SHAPE")
        if dest.shape != (2,):
            raise ValueError("DEST NOT CORRECT SHAPE")
        self._pos = pos
        self._vel = vel
        self._dest = dest
        self._orient = orient

    def __add__(self, other):
        # I am defining addition as the euclidian distance
        if (self.pos == other.pos).all():
            raise Exception("People are directly on top of each other")
        if type(other) != Person:
            raise TypeError("YOU CAN ONLY ADD PEOPLE")
        return distance.euclidean(self.pos, other.pos)

    @property
    def pos(self):
        return self._pos
    @property
    def vel(self):
        return self._vel
    @property
    def dest(self):
        return self._dest
    @property
    def orient(self):
        return self._orient

    @pos.setter
    def pos(self,val):
        if val.shape != (2,):
            raise ValueError("NOT CORRECT SHAPE")
        self._pos = val

    @vel.setter
    def vel(self,val):
        if val.shape != (2,):
            raise ValueError("NOT CORRECT SHAPE")
        self._vel = val

    @dest.setter
    def dest(self,val):
        if val.shape != (2,):
            raise ValueError("NOT CORRECT SHAPE" + str(val.shape))
        self._dest = val

    @orient.setter
    def orient(self,val):
        if type(val) != float:
            raise TypeError("orient set shit")
        self._orient = val

    @property
    def e_alpha(self):
        return (self.dest-self.pos)/np.linalg.norm(self.dest-self.pos)


def savepeopledata(filename,people):
    if type(people) != PeopleData:
        return TypeError("YOUR INPUT ISNT A PEOPLEDATA")
    with open(filename, "wb") as fh:
        fh.write(dumps(people))


def getdeopledata(filename):
    with open(filename, "rb") as fh:
        p = loads(fh.read())
    return p


def plotpeople(people):
    if type(people) != PeopleData:
        return TypeError("YOUR INPUT ISNT A PEOPLEDATA")

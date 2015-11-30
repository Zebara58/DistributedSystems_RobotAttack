from copy import copy, deepcopy
from threading import Thread
import threading
import logging
class Robot(Thread):
    def __init__(self, x, y, xSize, ySize, m, robotID, rules, condition):
        #Intialize
        #params: start x coord, start y coord, 
        self.x = x
        self.xSize = xSize
        self.ySize = ySize
        self.y = y
        self.robotID = robotID
        m.matrix[x][y] = robotID
        self.matrix = deepcopy(m.matrix)
        self.alive = True
        self.mainMap = m
        self.rules = rules
        self.cv = condition
        Thread.__init__(self)

        #if(x!=0):
        #	self.matrix[x-1][y] = m[x-1][y]
        #if(x!=xSize-1):
        #	self.matrix[x+1][y] = m[x+1][y]
        #if(y!=0):
        #	self.matrix[x][y-1] = m[x][y-1]
        #if(y!=ySize-1):
        #	self.matrix[x][y+1] = m[x][y+1]

    def run(self):
        logging.info('robot_'+str(self.robotID)+' started!');
        #with self.cv:
        logging.info('robot_'+str(self.robotID)+' with!');
        #with cv:
        while(self.alive):
            logging.info("start")
            self.move("d")
            logging.info("moved! "+str(self.robotID))
            #wait(10000)
            self.rules.inc()
            print("wait! "+str(self.robotID))
            #cv.wait()
            logging.info("get latest! "+str(self.robotID))
            self.getLatest()

        #wait(10000)
        logging.info('robot_'+str(self.robotID)+' finished!');


    def move(self, dir):
        prevLocX = self.x
        prevLocY = self.y
        if(dir=="r"):
            if(self.x!=self.xSize-1):
                self.matrix[self.x][self.y] = 0
                self.x = self.x+1
                self.matrix[self.x][self.y] = self.robotID
                
        if(dir=="l"):
            if(self.x!=0):
                self.matrix[self.x][self.y] = 0
                self.x = self.x-1
                self.matrix[self.x][self.y] = self.robotID
        if(dir=="d"):
            if(self.y!=self.ySize-1):
                self.matrix[self.x][self.y] = 0
                self.y = self.y+1
                self.matrix[self.x][self.y] = self.robotID
        if(dir=="u"):
            if(self.y!=0):
                self.matrix[self.x][self.y] = 0
                self.y = self.y-1
                self.matrix[self.x][self.y] = self.robotID
        #m.getLock()
        self.mainMap.update(self.x, self.y, prevLocX, prevLocY, self.robotID)
        #m.releaseLock()
        #self.wait()

    def getLatest(self):
        if(self.x!=0):
        	self.matrix[x-1][y] = self.mainMap[x-1][y]
        if(self.x!=self.xSize-1):
        	self.matrix[x+1][y] = self.mainMap[x+1][y]
        if(self.y!=0):
        	self.matrix[x][y-1] = self.mainMap[x][y-1]
        if(self.y!=ySize-1):
        	self.matrix[x][y+1] = self.mainMap[x][y+1]

    def printKnowledge(self):
        print(self.matrix)

    def printPos(self):
        print("X location = "+str(self.x))
        print("Y location = "+str(self.y))
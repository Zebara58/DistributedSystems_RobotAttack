from copy import copy, deepcopy
from threading import Thread
import threading
import time
import logging
from queue import *
class Robot(Thread):
    def __init__(self, x, y, xSize, ySize, m, robotID, rules, condition, numRobots):
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
        self.isLeader = False
        self.leaderFound = False
        self.numRobots = numRobots
        self.queue = Queue()
        self.moveQueue = Queue()


        #if(x!=0):
        #	self.matrix[x-1][y] = m[x-1][y]
        #if(x!=xSize-1):
        #	self.matrix[x+1][y] = m[x+1][y]
        #if(y!=0):
        #	self.matrix[x][y-1] = m[x][y-1]
        #if(y!=ySize-1):
        #	self.matrix[x][y+1] = m[x][y+1]

    def recieveMessage(self, message):
        logging.info("Robot"+str(self.robotID)+" recieved message! - "+str(message))
        if message[1] == "Elect leader":
            self.queue.put(message[0])
        elif message[1] == "Move":
            self.moveQueue.put(message[0])

    def robotConnectToNetwork(self, Network):
        self.network = Network

    #Elect self as leader if self has the lowest ID
    def electLeader(self):
        lowest = self.robotID
        #logging.info(str(self.queue.qsize()) +" queue size")
        while(not self.queue.empty()):
            cur = self.queue.get()
            logging.info("cur" + str(cur))
            if(cur<lowest):
                lowest = cur
        if(lowest == self.robotID):
            self.isLeader = True

    #Broadcast commands over the network to all robots
    #Move self
    def sendCommands(self):
        message = []
        message.append("d")
        message.append("Move")
        self.network.broadcastMessage(message)
        self.move("d")

    def logSelf(self, m):
        logging.info("Robot"+str(self.robotID)+" "+m)

    def run(self):
        logging.info('robot_'+str(self.robotID)+' started!')
        
        message = []
        message.append(self.robotID)
        message.append("Elect leader")
        self.network.broadcastMessage(message)
        #Wait for the messages for the election are recieved
        while(self.queue.qsize()!=(self.numRobots -1)):
            time.sleep(1)
        #logging.info(str(self.queue.qsize()) +" queue size")
        self.electLeader()
        logging.info('Leader elected!')
        if(self.isLeader):
            logging.info(str(self.robotID) + " is the leader!")
        time.sleep(1)

        with self.cv:

            logging.info('robot_'+str(self.robotID)+' with!');
            while(self.alive):
                logging.info("start")

                #if(self.isLeader):
                #    #Leader issue commands to other robots through the network
                #    #This also moves the leader
                #    self.sendCommands()
                #else:
                #    #Wait to recieve command from leader
                #    while(self.moveQueue.empty()):
                #        time.sleep(1)
                #    self.logSelf("About to move!")
                #    self.move(self.moveQueue.get())
                
                self.move("d")

                logging.info("moved! "+str(self.robotID))

                #wait(1)
                self.rules.inc()
                #print("wait! "+str(self.robotID))

                #Wait for all other robots to move by waiting for the Rules to notify that the round is over
                self.cv.wait()
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
        	self.matrix[self.x-1][self.y] = self.mainMap.matrix[self.x-1][self.y]
        if(self.x!=self.xSize-1):
        	self.matrix[self.x+1][self.y] = self.mainMap.matrix[self.x+1][self.y]
        if(self.y!=0):
        	self.matrix[self.x][self.y-1] = self.mainMap.matrix[self.x][self.y-1]
        if(self.y!=self.ySize-1):
        	self.matrix[self.x][self.y+1] = self.mainMap.matrix[self.x][self.y+1]

    def printKnowledge(self):
        print(self.matrix)

    def printPos(self):
        print("X location = "+str(self.x))
        print("Y location = "+str(self.y))


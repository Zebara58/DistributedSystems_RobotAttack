#Name: Kyle Brennan and Sean Kearney
#Date: 12/18/2015
#Class: CSCI 652
#Institution: Rochester Institute of Technology
#Description: This is the malicious robot that moves randomly to
#try to get to the goal.

from copy import copy, deepcopy
from threading import Thread
import threading
import time
import logging
from queue import *
import random
import math


class BadRobot(Thread):

    #Pre: This initializes the robot with: 
    #1. The x and y coordinate of the new robot
    #2. The x and y size of the board
    #3. The Map object pointer
    #4. The robot's ID
    #5. The Rules thread pointer
    #6. The condition object that is used by the Rules thread
    # to stop robots from taking multiple turns in a row

    #Post: This initializes the Robot.

    def __init__(self, x, y, xSize, ySize, m, robotID, rules, condition):
        #Initialize
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

        self.queue = Queue()
        self.moveQueue = Queue()
        self.goalFound = False
        self.goalX = -1
        self.goalY = -1
        self.robotList = {}
        self.leaderElected = False
        self.robotPlacement = []

        self.firstRunOf = True

        #CONFIGURATION for pathing
        self.sortAscendAfter = True
        self.reCalculatePosition = False

        self.placedRobotM ={}

        self.visited = []

        #if(x!=0):
        #	self.matrix[x-1][y] = m[x-1][y]
        #if(x!=xSize-1):
        #	self.matrix[x+1][y] = m[x+1][y]
        #if(y!=0):
        #	self.matrix[x][y-1] = m[x][y-1]
        #if(y!=ySize-1):
        #	self.matrix[x][y+1] = m[x][y+1]

    #Pre: Receive any message array with the requirement that the first
    #element is the robot ID who sent the message.
    #Post: This performs actions based on the message contents.
    def recieveMessage(self, message):
        #logging.info("Robot"+str(self.robotID)+" received message! - "+str(message))


        splitString = ""
        if(len(message)>3):
            splitString = str.split(message)
            if message[1] != "position":

                #shifted this if statement one tab right when adding encryption
                if(splitString[2] =="goal"):
                    self.goalX = int(splitString[0])
                    self.goalY = int(splitString[1])
                    self.logSelf("Malicious robot intercepted goal message at "+str(self.goalX) +" " + str(self.goalY))
                    print("Malicious robot intercepted goal message at "+str(self.goalX) +" " + str(self.goalY))
                    self.goalFound = True
                else:
                    self.logSelf("Malicious robot intercepted a message -> "+str(splitString[2]))
                    print("Malicious robot intercepted a message -> "+str(splitString[2]))
        #elif(message[1] == "position"):
        #    print("Malicious robot intercepted a position message!")

        self.logSelf("finished recieving message - "+str(message))
    
    def robotConnectToNetwork(self, Network):
        self.network = Network

    def addGoal(self, goal):
        self.goalX = goal[0]
        self.goalY = goal[1]
        self.goalFound = True
            
    def logSelf(self, m):
        logging.info("Robot"+str(self.robotID)+" "+m)

    #Post: This is the thread running for this robot.
    #Always move randomly and try to intercept goal messages.
    #Stop moving if the goal is seen.
    def run(self):
        self.visited.append(str(self.x) + " "+ str(self.y))
        logging.info('badRobot_'+str(self.robotID)+' started!')

        self.getLatest()

        while(self.alive):
            self.logSelf("start while")
            
            if(not self.goalFound):
                validPick = False
                while(not validPick):
                    pickNum = 3
                    pickI = random.randint(0,pickNum)
                    if(pickI==0):
                        validPick = self.move("d")
                    elif(pickI==1):
                        validPick = self.move("u")
                    elif(pickI==2):
                        validPick = self.move("l")
                    elif(pickI==3):
                        validPick = self.move("r")
                    if(not validPick):
                        pickNum-=1
                        if(pickNum<0):
                            break
           
            #self.move("d")

            #logging.info("moved! "+str(self.robotID))

            #wait(1)
            self.rules.inc()
            #print("wait! "+str(self.robotID))

            #Wait for all other robots to move by waiting for the Rules to notify that the round is over
            with self.cv:
                #logging.info('robot_'+str(self.robotID)+' with!');
                self.cv.wait()
            #logging.info("get latest! "+str(self.robotID))
            self.getLatest()

        #wait(10000)
        logging.info('robot_'+str(self.robotID)+' finished!');


    #Post: Move the robot based on the direction. Don't move to visited spots
    def move(self, dir):
        prevLocX = self.x
        prevLocY = self.y

        if(dir=="r"):
            if(self.x!=self.xSize-1):
                visitStr = str(self.x+1) + " "+ str(self.y)
                if(self.matrix[self.x+1][self.y]=="0" and (not visitStr in self.visited)):
                    self.x = self.x+1
                else:
                    #logging.error("move right blocked = self.matrix[self.x+1][self.y] " + str(self.matrix[self.x+1][self.y]))
                    return False

        elif(dir=="l"):
            if(self.x!=0):
                visitStr = str(self.x-1) + " "+ str(self.y)
                if(self.matrix[self.x-1][self.y]=="0" and (not visitStr in self.visited)):
                    self.x = self.x-1
                else:
                    #logging.error("move left blocked = self.matrix[self.x-1][self.y] " + str(self.matrix[self.x-1][self.y]))
                    return False
                    
        elif(dir=="d"):
            if(self.y!=self.ySize-1):
                visitStr = str(self.x) + " "+ str(self.y+1)
                if(self.matrix[self.x][self.y+1]=="0" and (not visitStr in self.visited)):
                    self.y = self.y+1
                else:
                    #logging.error("move down blocked = self.matrix[self.x][self.y+1] "+str(self.matrix[self.x][self.y+1]))
                    return False

        elif(dir=="u"):
            if(self.y!=0):
                visitStr = str(self.x) + " "+ str(self.y-1)
                if(self.matrix[self.x][self.y-1]=="0" and (not visitStr in self.visited)):
                    self.y = self.y-1
                else:
                    #logging.error("move up blocked = self.matrix[self.x][self.y-1] "+ str(self.matrix[self.x][self.y-1]))
                    return False

        #m.getLock()
        if(self.mainMap.update(self.x, self.y, prevLocX, prevLocY, self.robotID)):
            self.matrix[self.x][self.y] = str(self.robotID)
            self.matrix[prevLocX][prevLocY] = "0"
        else:
            self.x = prevLocX
            self.y = prevLocY
        #m.releaseLock()
        #self.wait()

        self.visited.append(str(self.x) + " "+ str(self.y))
        return True

    #Post: Get the latest from the main map.
    #If you see the goal and it has not been found,
    #then broadcast the goal location (encrypted)
    def getLatest(self):
        if(self.x!=0):
        	self.matrix[self.x-1][self.y] = self.mainMap.matrix[self.x-1][self.y]
        if(self.x!=self.xSize-1):
        	self.matrix[self.x+1][self.y] = self.mainMap.matrix[self.x+1][self.y]
        if(self.y!=0):
        	self.matrix[self.x][self.y-1] = self.mainMap.matrix[self.x][self.y-1]
        if(self.y!=self.ySize-1):
        	self.matrix[self.x][self.y+1] = self.mainMap.matrix[self.x][self.y+1]

        #check for goal
        #self.network.broadcastMessage(str(self.x-1)+" "+str(self.y)+ " goal")

        if not self.goalFound:
            if(self.x!=0 and self.matrix[self.x-1][self.y] == "g"):
                self.goalFound = True
            elif(self.x!=self.xSize-1 and self.matrix[self.x+1][self.y] == "g"):
                self.goalFound = True
            elif(self.y!=0 and self.matrix[self.x][self.y-1] == "g"):
                self.goalFound = True
            elif(self.y!=self.ySize-1 and self.matrix[self.x][self.y+1] == "g"):
                self.goalFound = True

    def printKnowledge(self):
        print(self.matrix)

    def printPos(self):
        print("X location = "+str(self.x))
        print("Y location = "+str(self.y))


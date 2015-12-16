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
        self.goalFound = False
        self.goalX = -1
        self.goalY = -1
        self.robotList = {}
        self.leaderElected = False

        #if(x!=0):
        #	self.matrix[x-1][y] = m[x-1][y]
        #if(x!=xSize-1):
        #	self.matrix[x+1][y] = m[x+1][y]
        #if(y!=0):
        #	self.matrix[x][y-1] = m[x][y-1]
        #if(y!=ySize-1):
        #	self.matrix[x][y+1] = m[x][y+1]

    def recieveMessage(self, message):
        #logging.info("Robot"+str(self.robotID)+" recieved message! - "+str(message))

        if message[1] == "Elect leader":
            self.queue.put(message[0])
        elif message[1] == "Move":
            if str(message[0]) == str(self.robotID):
                self.moveQueue.put(message[2])
        else:
            while(not self.leaderElected):
                self.logSelf("Waiting for leader to be elected")
                time.sleep(0.005)
            if(self.isLeader):  
                if(not self.goalFound and message[1] =="goal"):
                    self.goalX = message[0][0]
                    self.goalY = message[0][1]
                    self.logSelf("Leader found goal at "+str(self.goalX) +" " + str(self.goalY))
                elif(message[1] == "position"):
                    mesX = message[2][0]
                    mesY = message[2][1]
                    self.matrix[mesX][mesY] = str(message[0])
                    self.robotList[str(message[0])] = [mesX,mesY]
        self.logSelf("finished recieving message - "+str(message))
    def robotConnectToNetwork(self, Network):
        self.network = Network

    def addGoal(self, goal):
        self.goalX = goal[0]
        self.goalY = goal[1]
        self.goalFound = True

    #Elect self as leader if self has the lowest ID
    def electLeader(self):
        lowest = self.robotID
        #logging.info(str(self.queue.qsize()) +" queue size")
        while(not self.queue.empty()):
            cur = self.queue.get()
            #logging.info("cur" + str(cur))
            if(cur<lowest):
                lowest = cur

        if(lowest == self.robotID):
            self.isLeader = True
            self.pathList = []
            self.robotPlacement = []
            self.determineQuadrants()
        self.leaderElected = True

    def determineQuadrants(self):
        blar = "blark"
        
    #Broadcast commands over the network to all robots
    #Move self      
    def sendCommands(self):
        if self.goalFound:
            goalPlace = 0
            placed = 0
            ringNum = 1
            lowestRobot = self

            #only run if robotPlacement is empty
            if(len(self.robotPlacement)==0):
                logging.info("Running robotPlacement filling!")

                self.robotList[str(self.robotID)] = [self.x,self.y]
                #logging.info("robotList = "+str(self.robotList))
            
                tempRobotList = deepcopy(self.robotList)
                #logging.info("robotList deepcopy= "+str(tempRobotList))
                invalidPlace = False

                while(placed<len(self.robotList)):
                    lowest = 99999
                    i=-1
                    j=-1

                    #check if robot is in goal space
                    if(ringNum==1):
                        if(goalPlace==0):
                            gX = self.goalX
                            gY = self.goalY -1
                            if(gY>-1 and self.matrix[gX][gY]!="0"):
                                if self.matrix[gX][gY] in tempRobotList.keys():
                                    del tempRobotList[self.matrix[gX][gY]]
                                    self.robotPlacement.append([self.matrix[gX][gY], gX, gY])
                                    placed+=1
                                invalidPlace= True
                        elif(goalPlace == 1):     
                            gX = self.goalX
                            gY = self.goalY +1
                            if(gY<self.ySize and self.matrix[gX][gY]!="0"):
                                if self.matrix[gX][gY] in tempRobotList.keys():
                                    del tempRobotList[self.matrix[gX][gY]]
                                    self.robotPlacement.append([self.matrix[gX][gY], gX, gY])
                                    placed+=1
                                invalidPlace= True

                        elif(goalPlace == 2):
                            gX = self.goalX -1
                            gY = self.goalY
                            if(gX>-1 and self.matrix[gX][gY]!="0"):
                                if self.matrix[gX][gY] in tempRobotList.keys():
                                    del tempRobotList[self.matrix[gX][gY]]
                                    self.robotPlacement.append([self.matrix[gX][gY], gX, gY])
                                    placed+=1
                                invalidPlace= True
                        elif(goalPlace == 3):
                            gX = self.goalX +1
                            gY = self.goalY
                            if(gX<self.xSize and self.matrix[gX][gY]!="0"):
                                if self.matrix[gX][gY] in tempRobotList.keys():
                                    del tempRobotList[self.matrix[gX][gY]]
                                    self.robotPlacement.append([self.matrix[gX][gY], gX, gY])
                                    placed+=1
                                invalidPlace= True

                    

                    if((not invalidPlace) and goalPlace>3):
                        #have a loop from -ringNum to ringNum for x and y
                        #find what the x and y the goal place corespond to
                        tempGoalPlace = 0
                        foundRingPlace = False
                        for j in range(self.goalY-ringNum,self.goalY+ringNum+1):
                            if(j==self.goalY-ringNum or j == self.goalY+ringNum):
                                for i in range(self.goalX-ringNum,self.goalX+ringNum+1):
                                    #calculate position
                                    if tempGoalPlace+4 == goalPlace:
                                        #bounds checks
                                        if (i == self.goalX or j == self.goalY) or (i < 0 or i >= self.xSize) or (j < 0 or j >= self.ySize) or (self.mainMap.matrix[i][j]!="0"):
                                            invalidPlace = True
                                        #logging.info("Found ring place -> x="+str(i)+" y="+str(j))
                                        foundRingPlace = True
                                        break
                                    tempGoalPlace +=1
                            else:
                                for i in [self.goalX-ringNum, self.goalX+ringNum]:
                                    #calculate position
                                    if tempGoalPlace+4 == goalPlace:
                                        #bounds checks
                                        if (i == self.goalX or j == self.goalY) or (i < 0 or i >= self.xSize) or (j < 0 or j >= self.ySize) or (self.mainMap.matrix[i][j]!="0"):
                                            invalidPlace = True
                                        #logging.info("Found ring place -> x="+str(i)+" y="+str(j))
                                        foundRingPlace = True
                                        break
                                    tempGoalPlace +=1
                            if(foundRingPlace):
                                break
                    if not invalidPlace:
                        for r2key in tempRobotList:
                            #calc manhatttan distance from r2 to goal place
                            #returns the distance or -1 if invalid
                            if(goalPlace == 0):
                                #top
                                i = self.goalX
                                j = self.goalY-ringNum
                                if(j<0):
                                    dist= -1
                                else:
                                    dist=  self.calcBetweenTwoSpaces(self.goalX, self.goalY-ringNum, self.robotList[r2key][0], self.robotList[r2key][1])
                            elif(goalPlace == 1):
                                #bot
                                i = self.goalX
                                j = self.goalY+ringNum
                                if(j>=self.ySize):
                                    dist= -1
                                else:
                                    dist=  self.calcBetweenTwoSpaces(self.goalX, self.goalY+ringNum, self.robotList[r2key][0], self.robotList[r2key][1])
                            elif(goalPlace== 2):
                                #left
                                i = self.goalX-ringNum
                                j = self.goalY
                                if(i<0):
                                    dist= -1
                                else:
                                    dist=  self.calcBetweenTwoSpaces(self.goalX-ringNum, self.goalY, self.robotList[r2key][0], self.robotList[r2key][1])
                            elif(goalPlace == 3):
                                #right
                                i = self.goalX+ringNum
                                j = self.goalY
                                if(i>=self.xSize):
                                    dist= -1
                                else:
                                    dist=  self.calcBetweenTwoSpaces(self.goalX+ringNum, self.goalY, self.robotList[r2key][0], self.robotList[r2key][1])
                            else:
                                #we want to do the ring now 
                                tempRL = self.robotList[r2key]
                                dist= self.calcBetweenTwoSpaces(i,j, tempRL[0], tempRL[1])
                    
                            if(dist != -1):
                                if dist < lowest:
                                    lowest = dist
                                    lowestRobot = r2key
                                    lowestPlace = [i,j]
                            else:
                                invalidPlace = True
                                break

                        if not invalidPlace:
                            placed+=1
                            self.robotPlacement.append([lowestRobot, i, j])
                            #logging.info(tempRobotList)
                            del tempRobotList[lowestRobot]
                            #logging.info("tempRobotList after del "+str(tempRobotList))
                            #logging.info(str(lowestRobot) + " is the lowest robot with distance " + str(lowest) + " for space number " +str(goalPlace ) + " at location "+str(lowestPlace[0])+", "+str(lowestPlace[1]))
                
                    goalPlace+=1    
                    #multiple of 8 placements in each ring
                    if(goalPlace == (8*ringNum)+4):
                        ringNum+=1
                        goalPlace = 0
                    invalidPlace = False
            #logging.info(self.robotList)
            #message = [self.robotID, "Move", "d"]
            #self.network.broadcastMessage(message)
            #self.move("d")
        logging.info("robotPlacement = "+str(self.robotPlacement))
        for robotP in self.robotPlacement:
            tempRL = self.robotList[robotP[0]]
            self.findMoveAndSend(robotP[0], robotP[1],robotP[2], tempRL[0], tempRL[1])
        
    def findMoveAndSend(self, id, destX, destY, curX, curY):
        logging.info("MoveAndSend - id:"+str(id)+" destx:" +str(destX)+" destY:"+str(destY)+" curX:"+str(curX)+" curY:"+str(curY))
        self.pathList = []
        self.robotsMoved = []
        pathStr = ""
        validPath = False
        path = []
        xMove = curX
        yMove = curY
        #move down
        moveDown = False

        if(destY>curY):
            moveDown = True

        moveRight = False
        if(destX>curX):
            moveRight = True

        #simple case where you only need to go one direction 
        if(destX==curX and destY == curY):
            #no move
            logging.info("no move")
            pathStr = str(xMove)+" "+str(yMove)
            if(str(self.robotID) == id):
                self.move("n")
            else:
                self.network.broadcastMessage([id,"Move","n"])
        elif(destY==curY):
            if(moveRight):
                logging.info("right move")
                pathStr = str(xMove+1)+" "+str(yMove)
                if(str(self.robotID) == id):
                    self.move("r")
                else:
                    self.network.broadcastMessage([id,"Move","r"])
            else:
                logging.info("left move")
                pathStr = str(xMove-1)+" "+str(yMove)
                if(str(self.robotID) == id):
                    self.move("l")
                else:
                    self.network.broadcastMessage([id,"Move","l"])
        elif(destX==curX):
            if(moveDown):
                logging.info("down move")
                pathStr = str(xMove)+" "+str(yMove+1)
                if(str(self.robotID) == id):
                    self.move("d")
                else:
                    self.network.broadcastMessage([id,"Move","d"])
            else:
                logging.info("up move")
                pathStr = str(xMove)+" "+str(yMove-1)
                if(str(self.robotID) == id):
                    self.move("u")
                else:
                    self.network.broadcastMessage([id,"Move","u"])
        else:
            #DEBUGGING always move down
            #yMove +=1
            #pathStr = str(xMove)+" "+str(yMove)
            #if(str(self.robotID) == id):
            #    self.move("d")
            #else:
            #    self.network.broadcastMessage([id,"Move","d"])

            #consider both directions

            #move down to destination level
            if(moveDown):
                yMove +=1
                pathStr = str(xMove)+" "+str(yMove)
            
                if(pathStr in self.pathList):
                    #down path blocked so take a left or right

                    #reset yMove
                    yMove -= 1

                    if(moveRight):
                        xMove +=1
                    else:
                        xMove -=1
                    pathStr = str(xMove)+" "+str(yMove)
                    #Don't check board spot if filled or exists in path list. Just DO IT!
                    if(moveRight):
                        if(str(self.robotID) == id):
                            self.move("r")
                        else:
                            self.network.broadcastMessage([id,"Move","r"])
                    else:
                        if(str(self.robotID) == id):
                            self.move("l")
                        else:
                            self.network.broadcastMessage([id,"Move","l"])
                else:
                    #check if the space is filled and if that robot has already moved
                    #since we can't know current positions we have to assume that the robots 
                    #   followed commands and moved already
                    if(self.matrix[xMove][yMove]!="0"):
                        if(self.matrix[xMove][yMove] in self.robotsMoved):
                            if(str(self.robotID) == id):
                                self.move("d")
                            else:
                                self.network.broadcastMessage([id,"Move","d"])
                        else:
                            #Try left or right since the robot hasn't moved yet

                            #reset yMove
                            yMove -= 1

                            if(moveRight):
                                xMove +=1
                            else:
                                xMove -=1
                            pathStr = str(xMove)+" "+str(yMove)
                            #Don't check board spot if filled or exists in path list. Just DO IT!
                            if(moveRight):
                                if(str(self.robotID) == id):
                                    self.move("r")
                                else:
                                    self.network.broadcastMessage([id,"Move","r"])
                            else:
                                if(str(self.robotID) == id):
                                    self.move("l")
                                else:
                                    self.network.broadcastMessage([id,"Move","l"])
                    else:
                        if(str(self.robotID) == id):
                            self.move("d")
                        else:
                            self.network.broadcastMessage([id,"Move","d"])
            else:
                yMove -=1
                pathStr = str(xMove)+" "+str(yMove)
                if(pathStr in self.pathList):
                    #reset yMove
                    yMove += 1

                    if(moveRight):
                        xMove +=1
                    else:
                        xMove -=1
                    pathStr = str(xMove)+" "+str(yMove)
                    #Don't check board spot if filled or exists in path list. Just DO IT!
                    if(moveRight):
                        if(str(self.robotID) == id):
                            self.move("r")
                        else:
                            self.network.broadcastMessage([id,"Move","r"])
                    else:
                        if(str(self.robotID) == id):
                            self.move("l")
                        else:
                            self.network.broadcastMessage([id,"Move","l"])
                else:
                    #check if the space is filled and if that robot has already moved
                    #since we can't know current positions we have to assume that the robots 
                    #   followed commands and moved already
                    if(self.matrix[xMove][yMove]!="0"):
                        if(self.matrix[xMove][yMove] in self.robotsMoved):
                            if(str(self.robotID) == id):
                                self.move("u")
                            else:
                                self.network.broadcastMessage([id,"Move","u"])
                        else:
                            #Try left or right since the robot hasn't moved yet

                            #reset yMove
                            yMove -= 1

                            if(moveRight):
                                xMove +=1
                            else:
                                xMove -=1
                            pathStr = str(xMove)+" "+str(yMove)
                            #Don't check board spot if filled or exists in path list. Just DO IT!
                            if(moveRight):
                                if(str(self.robotID) == id):
                                    self.move("r")
                                else:
                                    self.network.broadcastMessage([id,"Move","r"])
                            else:
                                if(str(self.robotID) == id):
                                    self.move("l")
                                else:
                                    self.network.broadcastMessage([id,"Move","l"])
                    else:
                        if(str(self.robotID) == id):
                            self.move("u")
                        else:
                            self.network.broadcastMessage([id,"Move","u"])
        
        #Finished so append to pathList and to robotsMoved
        logging.info("sent command for id:"+str(id)+" for pathStr:"+pathStr)
        self.robotsMoved.append(id)
        if(pathStr in self.pathList):
            logging.info("Tried to add already existing path to past list.")
        else:
            self.pathList.append(pathStr)


            #for i in range(curY, destY+1):
            #    yMove -=1
            #    pathStr = str(id)+" "+str(xMove)+" "+str(yMove)

            #    #down path blocked
            #    if(pathStr in self.pathList):
            #        yMove += 1
            #        if(moveRight):
            #            xMove +=1
            #        else:
            #            xMove +=1
            #        pathStr = str(id)+" "+str(xMove)+" "+str(yMove)
            #        if(pathStr in self.pathList):
            #    path.append([destX, 
        #while(not validPath):

    def calcBetweenTwoSpaces(self, targetX, targetY, rx, ry):
        distance = abs(targetX-rx) + abs(targetY-ry)

        #Heuristic so that robots are assigned to a closer position
        distanceToGoal = abs(self.goalX-rx) + abs(self.goalY-ry)
        if(distanceToGoal<=distance):
            return distance*999
        return distance
            
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
            time.sleep(0.005)
        #logging.info(str(self.queue.qsize()) +" queue size")
        self.electLeader()
        #logging.info('Leader elected!')
        if(self.isLeader):
            logging.info(str(self.robotID) + " is the leader!")
        
        self.network.broadcastMessage([self.robotID, "position", [self.x,self.y]])
        time.sleep(.005)

        while(self.alive):
            self.logSelf("start while")
            if(self.isLeader):
                #Wait for recieving the positions of all robots
                while(len(self.robotList)<self.numRobots-1):
                    time.sleep(0.005)
                    #logging.info("robotList = "+str(self.robotList))
                #Leader issue commands to other robots through the network
                #This also moves the leader
                self.sendCommands()
            else:
                #Wait to recieve command from leader
                while(self.moveQueue.empty()):
                    time.sleep(0.005)
                self.logSelf("About to move!")
                self.move(self.moveQueue.get())
                
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


    def move(self, dir):
        prevLocX = self.x
        prevLocY = self.y
        if(dir=="r"):
            if(self.x!=self.xSize-1):
                if(self.matrix[self.x+1][self.y]=='0'):
                    self.matrix[self.x][self.y] = '0'
                    self.x = self.x+1
                    self.matrix[self.x][self.y] = str(self.robotID)

        elif(dir=="l"):
            if(self.x!=0):
                if(self.matrix[self.x-1][self.y]=='0'):
                    self.matrix[self.x][self.y] = '0'
                    self.x = self.x-1
                    self.matrix[self.x][self.y] = str(self.robotID)

        elif(dir=="d"):
            if(self.y!=self.ySize-1):
                if(self.matrix[self.x][self.y+1]=='0'):
                    self.matrix[self.x][self.y] = '0'
                    self.y = self.y+1
                    self.matrix[self.x][self.y] = str(self.robotID)

        elif(dir=="u"):
            if(self.y!=0):
                if(self.matrix[self.x][self.y-1]=='0'):
                    self.matrix[self.x][self.y] = '0'
                    self.y = self.y-1
                    self.matrix[self.x][self.y] = str(self.robotID)

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

        self.network.broadcastMessage([self.robotID, "position", [self.x,self.y]])

        #check for goal
        if not self.goalFound:
            if(self.x!=0 and self.matrix[self.x-1][self.y] == 'g'):
                self.network.broadcastMessage([[self.x-1,self.y], "goal"])
                self.goalFound = True
            elif(self.x!=self.xSize-1 and self.matrix[self.x+1][self.y] == 'g'):
                self.network.broadcastMessage([[self.x-1,self.y], "goal"])
                self.goalFound = True
            elif(self.y!=0 and self.matrix[self.x][self.y-1] == 'g'):
                self.network.broadcastMessage([[self.x,self.y+1], "goal"])
                self.goalFound = True
            elif(self.y!=self.ySize-1 and self.matrix[self.x][self.y+1] == 'g'):
                self.network.broadcastMessage([[self.x,self.y-1], "goal"])
                self.goalFound = True

    def printKnowledge(self):
        print(self.matrix)

    def printPos(self):
        print("X location = "+str(self.x))
        print("Y location = "+str(self.y))


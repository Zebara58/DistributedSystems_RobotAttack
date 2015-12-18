from copy import copy, deepcopy
from threading import Thread
import threading
import time
import logging
from queue import *
import random
import math

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
        self.robotPlacement = []

        #CONFIGURATION for pathing
        self.sortAscendAfter = True
        self.reCalculatePosition = False

        self.placedRobotM ={}

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
                    self.goalFound=True
                elif(message[1] == "position"):
                    mesX = message[2][0]
                    mesY = message[2][1]
                    if(message[0] in self.placedRobotM):
                        [xM,yM] = self.placedRobotM[message[0]]
                        self.matrix[xM][yM] = "0"
                    self.matrix[mesX][mesY] = str(message[0])
                    self.placedRobotM[message[0]] = [mesX,mesY]

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
            self.robotQuadrantAssignments = []
            
        self.leaderElected = True

    def determineQuadrants(self):

        if(self.xSize % 2 == 0):
            #if even board horizontal size, then
            self.leftSideVerticalSizeEnd = int(self.xSize/2) -1
        else: #is odd
            self.leftSideVerticalSizeEnd =int(self.xSize/2)

        #divide vertical distance by half the number of robots(half for each side)
        leftNumRobots = int(self.numRobots/2) #number of vertical spaces on each side
        rightNumRobots = self.numRobots - leftNumRobots #right side gets less in case of odd number

        #don't consider top rows (-2)
        leftSpacing = int(math.ceil((self.ySize-2)/leftNumRobots))
        if(leftSpacing<1):
            leftSpacing = 1

        #don't consider top rows (-2)
        rightSpacing = int(math.ceil((self.ySize-2)/rightNumRobots))
        if(rightSpacing<1):
            rightSpacing = 1

        logging.info("leftNumR="+str(leftNumRobots)+" rightNumR="+str(rightNumRobots)+" leftSpacing="+str(leftSpacing))

        #iterate through spaces, first i spaces assigned to first robot, next i spaces to second on that #side, etc
        #robots start in top left corner of their area
        #Also find the distance of each robot to the space and pick the closest for each robot

        quadrantStarts=[]
        #left side (don't consider top rows)
        y=1
        while(y<self.ySize-1):
            quadrantStarts.append([1,y])
            y+=leftSpacing
        #right side (don't consider top rows)
        y=1
        xEnd = self.xSize-2
        while(y<self.ySize-1):
            quadrantStarts.append([self.leftSideVerticalSizeEnd+2, y])
            y+=rightSpacing

        logging.info("robotList="+str(self.robotList))
        logging.info("Quadrant starts ="+str(quadrantStarts))
        self.robotQuadrantAssignments = []
        for rKey in self.robotList.keys():
            if(len(quadrantStarts)>0):
                [rx, ry] = self.robotList[rKey]
                lowestD = 999999
                closestQ = None
                for q in quadrantStarts:
                    distance = abs(q[0]-rx) + abs(q[1]-ry)
                    if(distance<lowestD):
                        lowestD = distance
                        closestQ = q
                quadrantStarts.remove(closestQ)
                self.robotQuadrantAssignments.append([rKey, closestQ[0], closestQ[1], False, False, False])
                #1st False = This is if the robot is doing the quadrant search currently
                #2nd False = This is if the robot reached the end of the quadrant
                #3rd False = This is if the robot is moving left then it is True otherise right
            else:
                break
        logging.info("Quadrants found! -"+str(self.robotQuadrantAssignments))


    #Broadcast commands over the network to all robots
    #Move self      
    def sendCommands(self):
        #logging.info("robotList = "+str(self.robotList))
        
        firstRunOf = True
        if(self.goalFound and firstRunOf):
            self.robotPlacement = []
            firstRunOf = False
        if self.goalFound and len(self.robotPlacement)==0:

            self.robotIDsPlaced= []
            goalPlace = 0
            placed = 0
            ringNum = 1
            lowestRobot = self


            self.robotPlacement = []

            logging.info("Running robotPlacement filling!")
            
            
            #logging.info("robotList deepcopy= "+str(tempRobotList))

            #This causes issues with robots hogging spaces!
            ##check if robot is in goal space
            #gX = self.goalX
            #gY = self.goalY -1
            #if(gY>-1 and self.matrix[gX][gY]!="0"):
            #    if self.matrix[gX][gY] in tempRobotList.keys():
            #        del tempRobotList[self.matrix[gX][gY]]
            #        self.robotPlacement.append([self.matrix[gX][gY], gX, gY, 0])
            #        placed+=1
   
            #gX = self.goalX
            #gY = self.goalY +1
            #if(gY<self.ySize and self.matrix[gX][gY]!="0"):
            #    if self.matrix[gX][gY] in tempRobotList.keys():
            #        del tempRobotList[self.matrix[gX][gY]]
            #        self.robotPlacement.append([self.matrix[gX][gY], gX, gY, 0])
            #        placed+=1


            #gX = self.goalX -1
            #gY = self.goalY
            #if(gX>-1 and self.matrix[gX][gY]!="0"):
            #    if self.matrix[gX][gY] in tempRobotList.keys():
            #        del tempRobotList[self.matrix[gX][gY]]
            #        self.robotPlacement.append([self.matrix[gX][gY], gX, gY, 0])
            #        placed+=1

            #gX = self.goalX +1
            #gY = self.goalY
            #if(gX<self.xSize and self.matrix[gX][gY]!="0"):
            #    if self.matrix[gX][gY] in tempRobotList.keys():
            #        del tempRobotList[self.matrix[gX][gY]]
            #        self.robotPlacement.append([self.matrix[gX][gY], gX, gY, 0])
            #        placed+=1
                
            invalidPlace= False

            #calculate positions list
            posList = []
            numAdded = 0
            robotPlacementTemp = []

            tempRobotList = []
            for rkey in self.robotList:
                tempRobotList.append(rkey)
            tempRobotList2 = deepcopy(tempRobotList)
            while(numAdded < self.numRobots):
                #ATTEMPT to move robots out of position to fill empty spot
                
                logging.info("starting loop again with numAdded ="+str(numAdded))
                top = [self.goalX, self.goalY-ringNum]
                bot = [self.goalX, self.goalY+ringNum]
                left = [self.goalX-ringNum, self.goalY]
                right = [self.goalX+ringNum, self.goalY]
                posList=[top, bot, left, right]

                toRemove = []
                for pos in posList:
                    if(pos[0]<0 or pos[0]>self.xSize-1 or pos[1]<0 or pos[1]>self.ySize-1):
                        toRemove.append(pos)
                for pos in toRemove:
                    posList.remove(pos)

                #calculate the cross poisitions and add them to robotPlacementTemp
                posListOrig = posList

                posListTemp = deepcopy(posList)
                numberOfCrossPositions = len(posList)
                #addedPosTemp = addedPos
                addedPos = 0
                while(addedPos<numberOfCrossPositions and numAdded<self.numRobots):
                    lowestDist = 999999
                    lowestRobot = None
                    lowestPos = None
                    for r2key in tempRobotList:
                        for pos in posListTemp:
                            tempRL = self.robotList[r2key]
                            dist= self.calcBetweenTwoSpaces(pos[0],pos[1], tempRL[0], tempRL[1])
                            if(dist<lowestDist):
                                lowestDist = dist
                                lowestRobot = r2key
                                lowestPos = pos
                
                    addedPos+=1
                    numAdded+=1

                    robotPlacementTemp.append([lowestRobot, lowestPos[0], lowestPos[1], lowestDist])

                    #logging.info(tempRobotList)
                    tempRobotList.remove(lowestRobot)
                    posListTemp.remove(lowestPos)
                    #logging.info("tempRobotList after del "+str(tempRobotList))
                    logging.info("TEMP ADD "+str(lowestRobot) + " is the lowest robot with distance " + str(lowestDist) + " for space number " +str(addedPos ) + " at location "+str(lowestPos[0])+", "+str(lowestPos[1]))

                

                #do ring spaces now

                #fill up posListTemp with ring spaces
                #have a loop from -ringNum to ringNum for x and y
                #find what the x and y the goal place corespond to
                #addedPos is the target space number
                # 0 | 1 | 2
                # 3 | G | 4
                # 5 | 6 | 7
                #the goal is to find what x and y addedPos corresponds to

                posListTemp = []
                tempCount = addedPos
                addedPos = 0
                while(addedPos < (8*ringNum) and tempCount<self.numRobots):
                    tempAddedPos = 0
                    invalidPlace = False
                    foundRingPlace = False
                    for j in range(self.goalY-ringNum,self.goalY+ringNum+1):
                        if(j==self.goalY-ringNum or j == self.goalY+ringNum):
                            for i in range(self.goalX-ringNum,self.goalX+ringNum+1):
                                #calculate position
                                if tempAddedPos == addedPos:
                                    #bounds checks
                                    if (i == self.goalX or j == self.goalY) or (i < 0 or i >= self.xSize) or (j < 0 or j >= self.ySize):
                                        invalidPlace = True
                                    #logging.info("Found ring place -> x="+str(i)+" y="+str(j))
                                    foundRingPlace = True
                                    break
                                tempAddedPos +=1
                        else:
                            for i in [self.goalX-ringNum, self.goalX+ringNum]:
                                #calculate position
                                if tempAddedPos == addedPos:
                                    #bounds checks
                                    if (i == self.goalX or j == self.goalY) or (i < 0 or i >= self.xSize) or (j < 0 or j >= self.ySize):
                                        invalidPlace = True
                                    #logging.info("Found ring place -> x="+str(i)+" y="+str(j))
                                    foundRingPlace = True
                                    break
                                tempAddedPos +=1
                        if(foundRingPlace):
                            break


                    addedPos+=1
                    if(foundRingPlace and not invalidPlace):
                        #add to posListTemp and posList
                        posListTemp.append([i,j])
                        posList.append([i,j])
                        tempCount+=1

                #multiple of 8 placements in each ring
                if(addedPos == (8*ringNum)):
                    ringNum+=1
                    addedPos = 0

                             
                #add  ring places to robotPlacementTemp
                #this only runs if there are robots left to fill up the ring
                logging.info("Starting add ring places to robotPlacementTemp with: tempRobotList="+str(tempRobotList)+ " posListTemp="+str(posListTemp))
                while(len(posListTemp)>0 and len(tempRobotList)>0):
                    lowestDist = 999999
                    lowestRobot = None
                    lowestPos = None
                    logging.info("Ring posListTemp:"+str(posListTemp)+" tempRobotList:"+str(tempRobotList))
                    for r2key in tempRobotList:
                        for pos in posListTemp:
                            tempRL = self.robotList[r2key]
                            dist= self.calcBetweenTwoSpaces(pos[0],pos[1], tempRL[0], tempRL[1])
                            if(dist<lowestDist):
                                lowestDist = dist
                                lowestRobot = r2key
                                lowestPos = pos

                    numAdded+=1

                    robotPlacementTemp.append([lowestRobot, lowestPos[0], lowestPos[1], lowestDist])

                    #logging.info(tempRobotList)
                    tempRobotList.remove(lowestRobot)
                    posListTemp.remove(lowestPos)
                    #logging.info("tempRobotList after del "+str(tempRobotList))
                    logging.info("TEMP ADD RING"+str(lowestRobot) + " is the lowest robot with distance " + str(lowestDist) + " at location "+str(lowestPos[0])+", "+str(lowestPos[1]))

                invalidPlace = False
                logging.info("done with ring - robotPlacementTemp="+str(robotPlacementTemp))

                

            #this is done to ensure empty spaces are assigned first   
            logging.info("before sort desc robotPlacementTemp "+str(robotPlacementTemp))
            robotPlacementTemp = sorted(robotPlacementTemp, key=lambda r: r[3], reverse = True)
            logging.info("after sort desc robotPlacementTemp "+str(robotPlacementTemp))

            logging.info("tempRobotList2="+str(tempRobotList2))
            #CAUSES robots to move out of spot and back into spot if run more than once
            addedPos = 0
            while(len(robotPlacementTemp)>0 and addedPos<len(posList) and addedPos<self.numRobots):
                lowestDist = 999999
                lowestRobot = None
                lowestPos = None
                pos=robotPlacementTemp[0]
                for robot in tempRobotList2:
                    tempRL = self.robotList[robot]
                    dist= self.calcBetweenTwoSpaces(pos[1],pos[2], tempRL[0], tempRL[1])
                    if(dist<lowestDist):
                        lowestDist = dist
                        lowestRobot = robot
                        lowestPos = [pos[1],pos[2]]
                
                addedPos+=1

                self.robotPlacement.append([lowestRobot, lowestPos[0], lowestPos[1], lowestDist])
                self.robotIDsPlaced.append(lowestRobot)
                del robotPlacementTemp[0]
                tempRobotList2.remove(lowestRobot)
                logging.info(str(lowestRobot) + " is the lowest robot with distance " + str(lowestDist) + " for space number " +str(addedPos ) + " at location "+str(lowestPos[0])+", "+str(lowestPos[1]))

            #logging.info(self.robotList)
            #message = [self.robotID, "Move", "d"]
            #self.network.broadcastMessage(message)
            #self.move("d")
        elif(not self.goalFound):
            #move to quadrant

            logging.info("Goal not found. Assigning quadrants.")

            self.robotIDsPlaced= []

            for q in self.robotQuadrantAssignments:
                
                r = self.robotList[q[0]]
                logging.info("r = "+str(r))
                logging.info("looking at quadrant = "+str(q))
                #1st False 3= This is if the robot is doing the quadrant search currently
                #2nd False 4= This is if the robot reached the end of the quadrant
                #3rd False 5= This is if the robot is moving left then it is True otherise right
                #if doing quadrant current
                if(q[3]==True):
                    if(r[1]==1 or r[1] == self.leftSideVerticalSizeEnd-1 or r[1] == self.leftSideVerticalSizeEnd+1 or r[1]==self.xSize-2):
                        #Move down since we reached the end of the quadrant

                        #Make sure we move down one more time
                        q[4] = True

                        self.network.broadcastMessage([q[0], "Move", "d"])
                    elif(q[4]==True):
                        #we need to move down again

                        #Switch directions
                        q[5] = not q[5]

                        q[4] = False

                        self.network.broadcastMessage([q[0], "Move", "d"])
                    elif(q[5]==True):
                        self.network.broadcastMessage([q[0], "Move", "l"])
                    else:
                        self.network.broadcastMessage([q[0], "Move", "r"])
                #else moving to quadarant
                else:
                    if(r[0]==q[1] and r[1]==q[2]):
                        q[3] = True
                        logging.info("Ready to start quadrant for r="+str(q[0]))
                        if(q[5]==True):
                            self.network.broadcastMessage([q[0], "Move", "l"])
                        else:
                            self.network.broadcastMessage([q[0], "Move", "r"])
                    else:
                        #do pathing to get to the quadrant start
                        logging.info("Pathing to quadrant for r="+str(q[0]))
                        self.robotPlacement.append([q[0], q[1], q[2], 1])
                self.robotIDsPlaced.append(q[0])

        if(self.sortAscendAfter):
            #robots closer to position move first
            logging.info("before sort ascend robotPlacement "+str(self.robotPlacement))
            self.robotPlacement = sorted(self.robotPlacement, key=lambda r: r[3])
            logging.info("after sort ascend robotPlacement "+str(self.robotPlacement))  
        else:
            #robots farther away move first  
            logging.info("before sort desc robotPlacement "+str(self.robotPlacement))
            robotPlacement = sorted(self.robotPlacement, key=lambda r: r[3], reverse = True)
            logging.info("after sort desc robotPlacement "+str(self.robotPlacement))

        #assign unassigned robots to not move
        for r in self.robotList.keys():
            if(not r in self.robotIDsPlaced):
                rTemp = self.robotList[r]
                rx, ry = rTemp[0], rTemp[1]
                rPTemp = [r, rx, ry, 0]
                logging.error("This robot was not placed - "+str(rPTemp))
                self.robotPlacement.append(rPTemp)
            

        logging.info("robotPlacement = "+str(self.robotPlacement))
        self.pathList = []
        self.robotsMoved = []

        self.destinationList = []
        for robotP in self.robotPlacement:
            tempRL = self.robotList[robotP[0]]
            self.calculatePathAndSend(robotP[0], robotP[1],robotP[2], tempRL[0], tempRL[1])
            logging.info("pathList after moving robot:"+str(robotP[0])+" = "+str(self.pathList))
        
        if(self.reCalculatePosition or not self.goalFound):
            self.robotPlacement = []
        
    #if you can't move vertically to the position y, then reduce yMove by 1
    #alters path
    def tryMoveVert(self, xMove, yMove, destY, moveDown, roundNum, path, pathStr):
        logging.info("tryMoveVert called with "+str([self, xMove, yMove, destY, moveDown, roundNum, path, pathStr]))
        logging.info("pathList="+str(self.pathList))
        logging.info("destinationList="+str(self.destinationList))
        
        while(yMove!=destY):

            if(moveDown):
                yMove+=1
            else:
                yMove-=1
            pStr = str(roundNum)+" "+str(xMove)+" "+str(yMove)
            pStr2 = str(xMove)+" "+str(yMove)
            #if(self.matrix[xMove][yMove] != "0"):
            if(pStr in self.pathList or pStr2 in self.destinationList or (xMove==self.goalX and yMove==self.goalY) or yMove<0 or yMove>self.ySize-1 or self.matrix[xMove][yMove]!="0"):
                #reset yMove
                roundNum-=1
                if(moveDown):
                    yMove-=1
                else:
                    yMove+=1
                
                logging.info("tryMoveVert failed with yMove="+str(yMove))
                if(pStr in self.pathList):
                    logging.info("pStr:"+str(pStr)+" in pathList:"+str(self.pathList))
                if(pStr2 in self.destinationList):
                    logging.info("pStr2:"+str(pStr2)+" in destinationList:"+str(self.destinationList))
                if(xMove==self.goalX and yMove==self.goalY):
                    logging.info("failed due to on goal")
                if(self.matrix[xMove][yMove]!="0"):
                    logging.info("failed due to space filled -"+str(self.matrix[xMove][yMove]))

                break
            else:
                path.append([roundNum, xMove, yMove])
                pathStr.append(str(roundNum)+" "+str(xMove)+" "+str(yMove))
                roundNum+=1
        logging.info("tryMoveVert finished and got ["+str(xMove)+" "+str(yMove)+"] with path ->"+str(path))
        return yMove, roundNum
    #if you can't move horizontally to the position, then reset xMove completely
    #alters path
    def tryMoveHor(self, xMove, yMove, destX, moveRight, roundNum, path, pathStr):	
        logging.info("matrix = "+str(self.matrix))
        logging.info("tryMoveHor called with "+str([self, xMove, yMove, destX, moveRight, roundNum, path, pathStr]))
        logging.info("pathList="+str(self.pathList))
        logging.info("destinationList="+str(self.destinationList))

        roundNumOrig = roundNum
        while(xMove!=destX):
            if(moveRight):
                xMove+=1
            else:
                xMove-=1
            #if(self.matrix[xMove][yMove] != "0"):
            pStr = str(roundNum)+" "+str(xMove)+" "+str(yMove)
            pStr2 = str(xMove)+" "+str(yMove)
            if(pStr in self.pathList or pStr2 in self.destinationList or (xMove==self.goalX and yMove==self.goalY)  or xMove<0 or xMove>self.ySize-1 or self.matrix[xMove][yMove]!="0"):

                roundNum = roundNumOrig
                logging.info("tryMoveHor failed with xMove="+str(xMove) +" and yMove="+str(yMove))
                if(pStr in self.pathList):
                    logging.info("pStr:"+str(pStr)+" in pathList:"+str(self.pathList))
                if(pStr2 in self.destinationList):
                    logging.info("pStr2:"+str(pStr2)+" in destinationList:"+str(self.destinationList))
                if(xMove==self.goalX and yMove==self.goalY):
                    logging.info("failed due to on goal")
                if(self.matrix[xMove][yMove]!="0"):
                    logging.info("failed due to space filled ="+str(self.matrix[xMove][yMove]))
                return -1, roundNum
            else:
                
                path.append([roundNum, xMove, yMove])
                pathStr.append(str(roundNum)+" "+str(xMove)+" "+str(yMove))
                roundNum+=1
        logging.info("tryMoveHor succeeded and got ["+str(xMove)+" "+str(yMove)+"]")
        return xMove, roundNum

    def calcArcPath(self, moveDown, curX, curY, xMove, yMove, destX, destY, savePathVert, savePathRound, savePathY):
        logging.info("Starting arc path past depth to dest Y for robot:"+str(id))
        #start moving past the goal and checking
        xMove = curX
            
        #restore max vert path
        
        path = savePathVert
        logging.info("path after restor = "+str(path))
        roundNum = savePathRound
        yMove = savePathY

        xCouldMove =True
        validPath = False
        path = []
        pathStr = []

        xPrev = xMove
        yPrev = yMove
        while(not validPath):
            if(moveDown):
                yMove+=1
            else:
                yMove-=1

            if(yMove<0 or yMove>self.ySize-1):
                logging.error("No valid arc path past depth due to going off board for robot:"+str(id)+"! Stuck on ["+str(xMove)+", "+str(yMove)+"] so do nothing")
                vaildPath = False
                break

            pStr = str(roundNum)+" "+str(xMove)+" "+str(yMove)
            pStr2 = str(xMove)+" "+str(yMove)
            #if(self.matrix[xMove][yMove] != "0"):
            if(pStr in self.pathList or pStr2 in self.destinationList or (xMove==self.goalX and yMove==self.goalY)):
                #reset yMove
                if(moveDown):
                    yMove-=1
                else:
                    yMove+=1
                logging.error("No valid arc path past depth due to collision for robot:"+str(id)+"! Stuck on ["+str(xMove)+", "+str(yMove)+"] so do nothing")
                vaildPath = False
                break
            else:
                roundNum+=1
                path.append([roundNum, xMove, yMove])
                pathStr.append(str(roundNum)+" "+str(xMove)+" "+str(yMove))
            moveRight = False
            if(xMove<destX):
                moveRight = True
            xMove, roundNum = self.tryMoveHor(xMove, yMove, destX, moveRight, roundNum, path, pathStr)

            if(xMove==-1):
                validPath = False
            else:
                #xMove made it to the destX so try moving up to goal (arc to goal from 'L')
                logging.info("Calling MoveVert arcPath for robot:"+str(id)+" xMove:"+str(xMove)+" yMove:"+str(yMove)+" not moveDown:"+str(moveDown))
                yMove, roundNum = self.tryMoveVert(xMove, yMove, destY, not moveDown, roundNum, path, pathStr)
                if(yMove == destY):
                    validPath = True
                break
        logging.info("arcPath done with path, pathStr, validPath, xMove, yMove "+str([path, pathStr, validPath, xMove, yMove]))
        return path, pathStr, validPath, xMove, yMove

    def calculatePathAndSend(self, id, destX, destY, curX, curY):
        logging.info("MoveAndSend - id:"+str(id)+" destx:" +str(destX)+" destY:"+str(destY)+" curX:"+str(curX)+" curY:"+str(curY))
        logging.info("robotList = "+str(self.robotList))
        pathStr = ""
        validPath = False
        path = []
        pathStr = []
        xMove = curX
        yMove = curY
        #move down
        moveDown = False

        if(destY>curY):
            moveDown = True

        moveRight = False
        if(destX>curX):
            moveRight = True
            
		#Calculate path
        prevX = xMove
        prevY = yMove

        roundNum = 1

        savePathVertSet = False
        savePathVert = []
        savePathRound = 1
        savePathY = curY

        xCouldMove = True
        while(not validPath):
            logging.info("Starting 'L' path for robot:"+str(id))  
            if(xCouldMove):
                if(destY<yMove):
                    moveDown = False
                else:
                    moveDown = True
                logging.info("Calling MoveVert 'L' for robot:"+str(id)+" xMove:"+str(xMove)+" yMove:"+str(yMove)+" moveDown:"+str(moveDown))
                yMove, roundNum = self.tryMoveVert(xMove, yMove, destY, moveDown, roundNum, path, pathStr)
            if(xMove!=destX):
                xMove, roundNum = self.tryMoveHor(xMove, yMove, destX, moveRight, roundNum, path, pathStr)

            if(xMove == destX and yMove == destY):
                validPath = True
                self.destinationList.append(str(xMove)+ " "+str(yMove))
                break
            elif((prevX==xMove and prevY == yMove) or yMove<0 or yMove>self.ySize-1):
                logging.error("No valid 'L' path for robot:"+str(id)+"! Stuck on ["+str(xMove)+", "+str(yMove)+"] so try arc path!")
                vaildPath = False
                break
            elif(xMove == -1):
                #couldn't get to goal with horizontal so backtrack

                #save path for later before reset by 1
                if(not savePathVertSet):
                    savePathVert = path
                    savePathRound = roundNum
                    savePathY = yMove
                    savePathVertSet = True

                yMove -=1
                if(yMove<0 or len(path)==0):
                    logging.error("No valid path #2 for robot:"+str(id)+"! Stuck on ["+str(xMove)+", "+str(yMove)+"] so try arc path!")
                    vaildPath = False
                    yMove = 0
                    break
                roundNum -=1
                xMove = prevX
                prevY = yMove
                xCouldMove = False
                del path[len(path)-1]
                del pathStr[len(path)-1]
            else:
                #do vertical again since xMove got to destX (this is a zig zag)
                prevX = xMove
                prevY = yMove
                xCouldMove = True

        if(not validPath):
            if(destY>curY):
                #move up for arc
                moveDown = False
            else:
                #move down for arc
                moveDown = True
            logging.info("path before restore = "+str(path))
            path, pathStr, validPath, xMove, yMove = self.calcArcPath(moveDown, curX, curY, xMove, yMove, destX, destY, savePathVert, savePathRound, savePathY)
            if(not validPath):
                path, pathStr, validPath, xMove, yMove = self.calcArcPath(not moveDown, curX, curY, xMove, yMove, destX, destY, savePathVert, savePathRound, savePathY)
        #repeat

        if(validPath):
            for p in pathStr:
                self.pathList.append(p)



        if(not validPath):
            logging.info("Do nothing path for robot:"+str(id)+"!")

            path =[]
            pathStr=[]

            self.moveBroadcast(curX, curY, id, "n") 
            self.pathList.append(str(1)+ " "+str(curX)+" "+str(curY))

      #      #pickI = random.randint(0,1)
      #      #if(pickI==0):
      #      #    if(moveDown):
      #      #        pathStr = self.moveBroadcast(xMove, yMove, id, "d")
      #      #    else:
      #      #        pathStr = self.moveBroadcast(xMove, yMove, id, "u")
      #      #else:
      #      #    if(moveRight):
      #      #        pathStr = self.moveBroadcast(xMove, yMove, id, "r")
      #      #    else:
      #      #        pathStr = self.moveBroadcast(xMove, yMove, id, "l")
        if(validPath):
            #determine direction from first move
            logging.info("Path found! - "+str(path))
            if(len(path)==0):
                logging.info("path actually isn't found!")
                pathStr = self.moveBroadcast(xMove, yMove, id, "n")
            else:
                if(path[0][2]>curY):
                    pathStr = self.moveBroadcast(xMove, yMove, id, "d")
                elif(path[0][1]>curX):
                    pathStr = self.moveBroadcast(xMove, yMove, id, "r")
                elif(path[0][2]<curY):
                    pathStr = self.moveBroadcast(xMove, yMove, id, "u")
                elif(path[0][1]<curX):
                    pathStr = self.moveBroadcast(xMove, yMove, id, "l")
                else:
                    logging.error("Impossible case! try to determine direction from 'n'")
                    pathStr = self.moveBroadcast(xMove, yMove, id, "n")
    def moveBroadcast(self, xMove, yMove, id, dir):
        logging.info(str(dir)+" move")
        pathStr = str(xMove)+" "+str(yMove)
        if(str(self.robotID) == id):
            self.move(dir)
        else:
            self.network.broadcastMessage([id,"Move",dir])

    def moveBroadcast2(self, id, dir):
        logging.info(str(dir)+" move")
        if(str(self.robotID) == id):
            self.move(dir)
        else:
            self.network.broadcastMessage([id,"Move",dir])

    def calcBetweenTwoSpaces(self, targetX, targetY, rx, ry):
        distance = abs(targetX-rx) + abs(targetY-ry)

        #Heuristic so that robots are assigned to a closer position
        distanceToGoal = abs(self.goalX-rx) + abs(self.goalY-ry)
        if(distanceToGoal<=distance):
            return distance*4
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

        self.getLatest()

        while(self.alive):
            self.logSelf("start while")
            if(self.isLeader):
                #Wait for recieving the positions of all robots
                while(len(self.robotList)<self.numRobots-1):
                    time.sleep(0.005)
                    #logging.info("robotList = "+str(self.robotList))
                
                self.robotList[str(self.robotID)] = [self.x,self.y]

                if(not self.goalFound and len(self.robotQuadrantAssignments) ==0):
                    self.determineQuadrants()
                #Leader issue commands to other robots through the network
                #This also moves the leader
                self.sendCommands()

                #reset robotList
                self.robotList = {}
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
                    self.x = self.x+1

        elif(dir=="l"):
            if(self.x!=0):
                if(self.matrix[self.x-1][self.y]=='0'):
                    self.x = self.x-1
                    
        elif(dir=="d"):
            if(self.y!=self.ySize-1):
                if(self.matrix[self.x][self.y+1]=='0'):
                    self.y = self.y+1

        elif(dir=="u"):
            if(self.y!=0):
                if(self.matrix[self.x][self.y-1]=='0'):
                    self.y = self.y-1

        #m.getLock()
        if(self.mainMap.update(self.x, self.y, prevLocX, prevLocY, self.robotID)):
            self.matrix[self.x][self.y] = str(self.robotID)
            self.matrix[prevLocX][prevLocY] = '0'
        else:
            self.x = prevLocX
            self.y = prevLocY
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
                self.network.broadcastMessage([[self.x+1,self.y], "goal"])
                self.goalFound = True
            elif(self.y!=0 and self.matrix[self.x][self.y-1] == 'g'):
                self.network.broadcastMessage([[self.x,self.y-1], "goal"])
                self.goalFound = True
            elif(self.y!=self.ySize-1 and self.matrix[self.x][self.y+1] == 'g'):
                self.network.broadcastMessage([[self.x,self.y+1], "goal"])
                self.goalFound = True

    def printKnowledge(self):
        print(self.matrix)

    def printPos(self):
        print("X location = "+str(self.x))
        print("Y location = "+str(self.y))


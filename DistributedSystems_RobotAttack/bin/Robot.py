from copy import copy, deepcopy
from threading import Thread
import threading
import time
import logging
from queue import *
import random

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

            self.robotList[str(self.robotID)] = [self.x,self.y]
            #logging.info("robotList = "+str(self.robotList))


            #only run if robotPlacement is empty
            #if(len(self.robotPlacement)==0):
            self.robotPlacement = []
            if(True):
                logging.info("Running robotPlacement filling!")
            
                tempRobotList = deepcopy(self.robotList)
                #logging.info("robotList deepcopy= "+str(tempRobotList))

                #check if robot is in goal space
                gX = self.goalX
                gY = self.goalY -1
                if(gY>-1 and self.matrix[gX][gY]!="0"):
                    if self.matrix[gX][gY] in tempRobotList.keys():
                        del tempRobotList[self.matrix[gX][gY]]
                        self.robotPlacement.append([self.matrix[gX][gY], gX, gY, 0])
                        placed+=1
   
                gX = self.goalX
                gY = self.goalY +1
                if(gY<self.ySize and self.matrix[gX][gY]!="0"):
                    if self.matrix[gX][gY] in tempRobotList.keys():
                        del tempRobotList[self.matrix[gX][gY]]
                        self.robotPlacement.append([self.matrix[gX][gY], gX, gY, 0])
                        placed+=1


                gX = self.goalX -1
                gY = self.goalY
                if(gX>-1 and self.matrix[gX][gY]!="0"):
                    if self.matrix[gX][gY] in tempRobotList.keys():
                        del tempRobotList[self.matrix[gX][gY]]
                        self.robotPlacement.append([self.matrix[gX][gY], gX, gY, 0])
                        placed+=1

                gX = self.goalX +1
                gY = self.goalY
                if(gX<self.xSize and self.matrix[gX][gY]!="0"):
                    if self.matrix[gX][gY] in tempRobotList.keys():
                        del tempRobotList[self.matrix[gX][gY]]
                        self.robotPlacement.append([self.matrix[gX][gY], gX, gY, 0])
                        placed+=1
                
                invalidPlace= False

                while(placed<len(self.robotList)):
                    lowest = 99999
                    i=-1
                    j=-1

                    if(goalPlace>3):
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
                            self.robotPlacement.append([lowestRobot, i, j, lowest])
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
        self.pathList = []
        self.robotsMoved = []

        #sort robotPlacement by distance
        self.robotPlacement = self.quickSort(self.robotPlacement)
        logging.info("robotPlacement after sort = "+str(self.robotPlacement))

        for robotP in self.robotPlacement:
            tempRL = self.robotList[robotP[0]]
            self.destinationList = []
            self.calculatePathAndSend(robotP[0], robotP[1],robotP[2], tempRL[0], tempRL[1])

    #Source: http://stackoverflow.com/questions/18262306/quick-sort-with-python
    def quickSort(self, array):
        less = []
        equal = []
        greater = []

        if len(array) > 1:
            pivot = array[0][3]
            for x in array:
                if x[3] < pivot:
                    less.append(x)
                if x[3] == pivot:
                    equal.append(x)
                if x[3] > pivot:
                    greater.append(x)
            # Don't forget to return something!
            return self.quickSort(less)+equal+self.quickSort(greater)  # Just use the + operator to join lists
        # Note that you want equal ^^^^^ not pivot
        else:  # You need to hande the part at the end of the recursion - when you only have one element in your array, just return the array.
            return array

    #if you can't move vertically to the position y, then reduce yMove by 1
    #alters path
    def tryMoveVert(self, xMove, yMove, destY, moveDown, roundNum, path, pathStr):
        while(yMove!=destY):
            if(moveDown):
                yMove+=1
            else:
                yMove-=1
            pStr = str(roundNum)+" "+str(xMove)+" "+str(yMove)
            pStr2 = str(xMove)+" "+str(yMove)
            #if(self.matrix[xMove][yMove] != "0"):
            if(pStr in self.pathList or pStr2 in self.destinationList):
                #reset yMove
                roundNum-=1
                if(moveDown):
                    yMove-=1
                else:
                    yMove+=1
                break
            else:
                roundNum+=1
                path.append([roundNum, xMove, yMove])
                pathStr.append(str(roundNum)+" "+str(xMove)+" "+str(yMove))
        logging.info("tryMoveVert finished and got ["+str(xMove)+" "+str(yMove)+"]")
        return yMove, roundNum
    #if you can't move horizontally to the position, then reset xMove completely
    #alters path
    def tryMoveHor(self, xMove, yMove, destX, moveRight, roundNum, path, pathStr):	
        roundNumOrig = roundNum
        while(xMove!=destX):
            if(moveRight):
                xMove+=1
            else:
                xMove-=1
            #if(self.matrix[xMove][yMove] != "0"):
            pStr = str(roundNum)+" "+str(xMove)+" "+str(yMove)
            pStr2 = str(xMove)+" "+str(yMove)
            if(pStr in self.pathList or pStr2 in self.destinationList):
                #reset yMove
                roundNum = roundNumOrig
                logging.info("tryMoveVert failed")
                return -1
            else:
                roundNum+=1
                path.append([roundNum, xMove, yMove])
                pathStr.append(str(roundNum)+" "+str(xMove)+" "+str(yMove))
        logging.info("tryMoveHor succeeded and got ["+str(xMove)+" "+str(yMove)+"]")
        return xMove, roundNum

    def calculatePathAndSend(self, id, destX, destY, curX, curY):
        logging.info("MoveAndSend - id:"+str(id)+" destx:" +str(destX)+" destY:"+str(destY)+" curX:"+str(curX)+" curY:"+str(curY))
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
                yMove, roundNum = self.tryMoveVert(xMove, yMove, destY, moveDown, roundNum, path, pathStr)
            xMove, roundNum = self.tryMoveHor(xMove, yMove, destX, moveRight, roundNum, path, pathStr)

            if(xMove == destX and yMove == destY):
                validPath = True
                self.destinationList.append(str(xMove)+ " "+str(yMove))
                break
            elif((prevX==xMove and prevY == yMove) or yMove<0):
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
                if(yMove<0):
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
                #do vertical again since xMove got to destX
                prevX = xMove
                prevY = yMove
                xCouldMove = True

        #if(not validPath):
        #    logging.info("Starting arc path past depth to dest Y for robot:"+str(id))
        #    #start moving past the goal and checking
        #    xMove = curX
            
        #    #restore max vert path
        #    path = savePathVert
        #    roundNum = savePathRound
        #    yMove = savePathY

        #    xCouldMove =True
        #    validPath = False

        #    xPrev = xMove
        #    yPrev = yMove
        #    while(not validPath):
        #        if(moveDown):
        #            yMove+=1
        #        else:
        #            yMove-=1

        #        if(yMove<0 or yMove>self.ySize):
        #            logging.error("No valid arc path past depth due to going off board for robot:"+str(id)+"! Stuck on ["+str(xMove)+", "+str(yMove)+"] so do nothing")
        #            vaildPath = False
        #            break

        #        pStr = str(roundNum)+" "+str(xMove)+" "+str(yMove)
        #        pStr2 = str(xMove)+" "+str(yMove)
        #        #if(self.matrix[xMove][yMove] != "0"):
        #        if(pStr in self.pathList or pStr2 in self.destinationList):
        #            #reset yMove
        #            if(moveDown):
        #                yMove-=1
        #            else:
        #                yMove+=1
        #            logging.error("No valid arc path past depth due to collision for robot:"+str(id)+"! Stuck on ["+str(xMove)+", "+str(yMove)+"] so do nothing")
        #            vaildPath = False
        #            break
        #        else:
        #            roundNum+=1
        #            path.append([roundNum, xMove, yMove])
        #            pathStr.append(str(roundNum)+" "+str(xMove)+" "+str(yMove))

        #        xMove, roundNum = self.tryMoveHor(xMove, yMove, destX, moveRight, roundNum, path, pathStr)

        #        if(xMove==-1):
        #            validPath = False
        #        else:
        #            #xMove made it to the destX so try moving up to goal (arc to goal from 'L')
        #            yMove, roundNum = tryMoveVert(self, xMove, yMove, destY, not moveDown, roundNum, path)
        #            if(yMove == destY):
        #                validPath = True
        #            break

        if(validPath):
            for p in pathStr:
                self.pathList.append(p)



        if(not validPath):
            logging.info("Do nothing path for robot:"+str(id)+"!")
            self.moveBroadcast(curX, curY, id, "n") 
            self.pathList.append(str(1)+ " "+str(curX)+" "+str(curY))
      #      #Try looking for a path in the less efficient direction
      #      logging.info("For robot:"+str(id)+" checking less efficient direction")
      #      validPath = False
      #      path = []
      #      xMove = curX
      #      yMove = curY
      #      #move down
      #      pickRandom = False

      #      #Do opposite 
      #      moveDown = not moveDown
            
		    ##Calculate path
      #      #do opposite direction


      #      
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
                pathStr = self.moveBroadcast(xMove, yMove, id, "n")
            elif(moveDown):
                if(path[0][2]>curY):
                    pathStr = self.moveBroadcast(xMove, yMove, id, "d")
                elif(path[0][1]>curX):
                    pathStr = self.moveBroadcast(xMove, yMove, id, "r")
                else:
                    pathStr = self.moveBroadcast(xMove, yMove, id, "l")
            else:
                if(path[0][2]<curY):
                    pathStr = self.moveBroadcast(xMove, yMove, id, "u")
                elif(path[0][1]>curX):
                    pathStr = self.moveBroadcast(xMove, yMove, id, "r")
                else:
                    pathStr = self.moveBroadcast(xMove, yMove, id, "l")

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
            return distance*2
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
                    self.matrix[self.x][self.y] = '0'
                    self.x = self.x+1

        elif(dir=="l"):
            if(self.x!=0):
                if(self.matrix[self.x-1][self.y]=='0'):
                    self.matrix[self.x][self.y] = '0'
                    self.x = self.x-1
                    
        elif(dir=="d"):
            if(self.y!=self.ySize-1):
                if(self.matrix[self.x][self.y+1]=='0'):
                    self.matrix[self.x][self.y] = '0'
                    self.y = self.y+1

        elif(dir=="u"):
            if(self.y!=0):
                if(self.matrix[self.x][self.y-1]=='0'):
                    self.matrix[self.x][self.y] = '0'
                    self.y = self.y-1

        #m.getLock()
        if(self.mainMap.update(self.x, self.y, prevLocX, prevLocY, self.robotID)):
            self.matrix[self.x][self.y] = str(self.robotID)
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


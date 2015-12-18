import logging
import random
import threading
class Map:
    
    def __init__(self, xSize, ySize):
        self.matrix = [["0" for x in range(xSize)] for y in range(ySize)]
        #self.matrix[3][3] = 1
        #self.matrix[1][0] = 1
        #self.lock = threading.Lock()
        self.xSize = xSize
        self.ySize = ySize
        self.goalX = goalX
        self.goalY = goalY

        #set goal

        self.matrix[self.goalX][self.goalY] = "g"
        self.goal = [self.goalX,self.goalY]

        self.lock = threading.Lock()

    def checkIfFilled(self, x, y):
        if self.matrix[x][y] == "0":
            return False
        else:
            return True

    def print(self):
        for y in range(self.ySize):
            string = ""
            for x in range(self.xSize):
                string += str(self.matrix[x][y]) + "  "
            print(string)
        print("*****************************************")

    #def getLock(self):
    #    self.lock.acquire()

    #def releaseLock(self):
    #    self.lock.release()

    def update(self, curX, curY, prevX, prevY, id):
        self.lock.acquire(True)
        try:  
    
            if(self.matrix[curX][curY]=="0"):
                self.matrix[prevX][prevY] = "0"
                #check for malicious robot location here
                self.matrix[curX][curY] = id
                logging.info("update for "+str(id)+" curX-"+str(curX)+"  curY-"+str(curY)+ "  prevX-"+str(prevX)+"  prevY-"+str(prevY))
                return True
            else:
                return False
        finally:
            self.lock.release()
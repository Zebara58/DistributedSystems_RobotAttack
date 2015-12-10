import logging
import random
class Map:
    def __init__(self, xSize, ySize):
        self.matrix = [['0' for x in range(xSize)] for y in range(ySize)]
        #self.matrix[3][3] = 1
        #self.matrix[1][0] = 1
        #self.lock = threading.Lock()
        self.xSize = xSize
        self.ySize = ySize

        #set goal
        ranX = random.randint(0,xSize-1)
        ranY = random.randint(0,ySize-1)

        self.matrix[ranX][ranY] = 'g'
        
    def checkIfFilled(self, x, y):
        if self.matrix[x][y] == '0':
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
        self.matrix[prevX][prevY] = '0'
        #check for malicious robot location here
        self.matrix[curX][curY] = id
        logging.info("update for "+str(id)+" curX-"+str(curX)+"  curY-"+str(curY)+ "  prevX-"+str(prevX)+"  prevY-"+str(prevY))
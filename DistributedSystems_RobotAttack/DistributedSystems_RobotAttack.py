from copy import copy, deepcopy
import threading
#Robot/malicious in matrix is 1
#Empty spaces is 0
#Goal is 2

xSize = 5
ySize = 5

#Matrix[y][x]
class Map:
    def __init__(self, xSize, ySize):
        self.matrix = [[0 for x in range(xSize)] for y in range(ySize)]
        #self.matrix[3][3] = 1
        #self.matrix[1][0] = 1
        self.lock = threading.Lock()
        self.xSize = xSize
        self.ySize = ySize
        

    def print(self):
        for y in range(self.ySize):
            string = ""
            for x in range(self.xSize):
                string += str(self.matrix[x][y]) + "  "
            print(string)

    def getLock(self):
        self.lock.acquire()

    def releaseLock(self):
        self.lock.release()

    def update(self, curX, curY, prevX, prevY, id):
        self.matrix[prevX][prevY] = 0
        #check for malicious robot location here
        self.matrix[curX][curY] = id

class Robot:
    def __init__(self, x, y, xSize, ySize, m, robotID):
        #Intialize
        #params: start x coord, start y coord, 
        self.x = x
        self.xSize = xSize
        self.ySize = ySize
        self.y = y
        self.robotID = robotID
        m.matrix[x][y] = robotID
        self.matrix = deepcopy(m.matrix)

        #if(x!=0):
        #	self.matrix[x-1][y] = m[x-1][y]
        #if(x!=xSize-1):
        #	self.matrix[x+1][y] = m[x+1][y]
        #if(y!=0):
        #	self.matrix[x][y-1] = m[x][y-1]
        #if(y!=ySize-1):
        #	self.matrix[x][y+1] = m[x][y+1]

    def move(self, dir, m):
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
        m.getLock()
        m.update(self.x, self.y, prevLocX, prevLocY, self.robotID)
        m.releaseLock()
        #self.wait()

    def getLatest(self, m):
        if(x!=0):
        	self.matrix[x-1][y] = m[x-1][y]
        if(x!=xSize-1):
        	self.matrix[x+1][y] = m[x+1][y]
        if(y!=0):
        	self.matrix[x][y-1] = m[x][y-1]
        if(y!=ySize-1):
        	self.matrix[x][y+1] = m[x][y+1]

    def printKnowledge(self):
        print(self.matrix)

    def printPos(self):
        print("X location = "+str(self.x))
        print("Y location = "+str(self.y))

m = Map(xSize, ySize)

r1 = Robot(0,0,xSize,ySize,m, 1)
r2 = Robot(1,1,xSize,ySize,m, 2)

m.print()
r1.move("r", m)
r2.move("d", m)

#r1.printKnowledge()
r1.printPos()
m.print()
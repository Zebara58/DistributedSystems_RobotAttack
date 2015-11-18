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
        self.matrix[3][3] = 1
        self.matrix[1][0] = 1
        self.lock = threading.Lock()

    def print():
        print(self.matrix)

    def getLock():
        lock.acquire()

    def releaseLock():
        lock.release()

class Robot:
    def __init__(self, x, y, xSize, ySize, m, robotID):
        #Intialize
        #params: start x coord, start y coord, 
        self.x = x
        self.xSize = xSize
        self.ySize = ySize
        self.y = y
        self.robotID = robotID
        m[x][y] = robotID
        self.matrix = deepcopy(m)

        #if(x!=0):
        #	self.matrix[x-1][y] = m[x-1][y]
        #if(x!=xSize-1):
        #	self.matrix[x+1][y] = m[x+1][y]
        #if(y!=0):
        #	self.matrix[x][y-1] = m[x][y-1]
        #if(y!=ySize-1):
        #	self.matrix[x][y+1] = m[x][y+1]

    def move(self, dir, m):

        if(dir=="r"):
            if(self.x!=self.xSize-1):
                self.matrix[self.x][self.y] = 0
                self.x = self.x+1
                self.matrix[self.x][self.y] = robotID
                
        if(dir=="l"):
            if(self.x!=0):
                self.matrix[self.x][self.y] = 0
                self.x = self.x-1
                self.matrix[self.x][self.y] = robotID
        if(dir=="d"):
            if(self.y!=self.ySize-1):
                self.matrix[self.x][self.y] = 0
                self.y = self.y+1
                self.matrix[self.x][self.y] = robotID
        if(dir=="u"):
            if(self.y!=0):
                self.matrix[self.x][self.y] = 0
                self.y = self.y-1
                self.matrix[self.x][self.y] = robotID

    def update(self, m):
        if(x!=0):
        	self.matrix[x-1][y] = m[x-1][y]
        if(x!=xSize-1):
        	self.matrix[x+1][y] = m[x+1][y]
        if(y!=0):
        	self.matrix[x][y-1] = m[x][y-1]
        if(y!=ySize-1):
        	self.matrix[x][y+1] = m[x][y+1]
        m.getLock()
        m.update(self.matrix)
    def printKnowledge(self):
        print(self.matrix)

    def printPos(self):
        print("X location = "+self.x)
        print("Y location = "+self.y)

m = Map(xSize, ySize)

r1 = Robot(0,0,xSize,ySize,m)

m.print()
r1.move("r", m)
r1.printKnowledge()
r1.printPos()

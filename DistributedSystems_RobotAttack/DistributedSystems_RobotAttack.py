from copy import copy, deepcopy
#Robot/malicious in matrix is 1
#Empty spaces is 0
#Goal is 2

xSize = 5
ySize = 5

#Matrix[y][x]
matrix = [[0 for x in range(xSize)] for y in range(ySize)]
matrix[3][3] = 1
matrix[1][0] = 1
class Robot:
    def __init__(self, x, y, xSize, ySize, m):
        #Intialize
        #params: start x coord, start y coord, 
        self.x = x
        self.xSize = xSize
        self.ySize = ySize
        self.y = y
        m[x][y] = 1
        self.matrix = deepcopy(m)

        #if(x!=0):
        #	self.matrix[x-1][y] = m[x-1][y]
        #if(x!=xSize-1):
        #	self.matrix[x+1][y] = m[x+1][y]
        #if(y!=0):
        #	self.matrix[x][y-1] = m[x][y-1]
        #if(y!=ySize-1):
        #	self.matrix[x][y+1] = m[x][y+1]

    def move(self, dir):
        if(dir=="r"):
            if(self.x!=self.xSize-1):
                self.x = self.x+1

    def printKnowledge(self):
        print(self.matrix)

    def printPos(self):
        print("X location = "+self.x)
        print("Y location = "+self.y)

r1 = Robot(0,0,xSize,ySize,matrix)

print(matrix)
r1.move("r")
r1.printKnowledge()
r1.printPos()

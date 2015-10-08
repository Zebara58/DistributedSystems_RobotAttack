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
		self.x = x
		self.xSize = xSize
		self.ySize = ySize
		self.y = y
		m[x][y] = 1
		self.matrix = deepcopy(m)
		if(x!=0):
			self.matrix[x-1][y] = m[x-1][y]
		if(x!=xSize-1):
			self.matrix[x+1][y] = m[x+1][y]
		if(y!=0):
			self.matrix[x][y-1] = m[x][y-1]
		if(y!=ySize-1):
			self.matrix[x][y+1] = m[x][y+1]

	def move(self):
		self.matrix[2][2] = 1
		
	def printKnowledge(self):
		print(self.matrix)

r1 = Robot(0,0,xSize,ySize,matrix)


r1.move()
r1.printKnowledge()
print(matrix)

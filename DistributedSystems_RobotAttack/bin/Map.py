#Name: Kyle Brennan and Sean Kearney
#Date: 12/18/2015
#Class: CSCI 652
#Institution: Rochester Institute of Technology
#Description: This is the main map object that is printed to the terminal. 
#Robots update the main map after they move. The Map object locks for each update.
#The Map object stops invalid updates to the main map.

import logging
import random
import threading
class Map:
    
    #Pre: This takes the board size (the x and y size) along with the goal x and y position.
    #Post: Initializes the main map with the specified size and goal.
    def __init__(self, xSize, ySize, goalX, goalY):
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

    #Pre: This takes an x and y coordinate.
    #Post: This returns True if that position is filled and False otherwise.
    def checkIfFilled(self, x, y):
        if self.matrix[x][y] == "0":
            return False
        else:
            return True

    #Post: This prints out the main map to the termnial.
    def print(self):
        for y in range(self.ySize):
            string = ""
            for x in range(self.xSize):
                string += str(self.matrix[x][y]) + "  "
            print(string)
        print("*****************************************")


    #Pre: This takes the current X and Y that the robot tried to move to.
    #This also takes the previous X and Y position of the robot so that position can
    #be reset to "0". Finally, the ID of the robot is taken so that the 
    #robot can be placed on a new spot on the board.
    #Post: This updates the main map with the new X and Y position of the robot
    #if that position is valid. Returns True if success and False otherwise. 
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
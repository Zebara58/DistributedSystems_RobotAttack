#Name: Kyle Brennan and Sean Kearney
#Date: 12/18/2015
#Class: CSCI 652
#Institution: Rochester Institute of Technology
#Description: This is a multithreaded application to coordinate virtual robots with 
#malicious robots to surround a goal location with or without knowing where the 
#goal is. The robots cannot directly communicate with each other and each robot 
#broadcasts messages through the network object to all other robots. To coordinate 
#the robots, the bully algorithm is utilized to elect a leader who dictates all 
#robot movement. If the goal is not known, then a scanning search algorithm is used 
#to find the goal. If the goal is found, then robots are assigned once to a position 
#around the goal. The leader recalculates the path of each robot to the goal after 
#each move. To stop malicious robots from receiving commands or the goal position, 
#encryption is utilized. This algorithm gets the robots to the goal in efficient 
#time to beat the malicious robots to the goal.


from threading import Thread
import threading
from Map import Map
from Robot import Robot
from Rules import Rules
from Network import Network
from BadRobot import BadRobot
import os
import random
from cipher import *


#Robot/malicious in matrix is robotID
#Empty spaces is 0
#Goal is g

#Matrix[x][y]
import time
import random
def checkRobotPlacement(m):
    full = True
    while full:
        xRand = random.randint(0, xSize-1)
        yRand = random.randint(0, ySize-1)
        full = m.checkIfFilled(xRand,yRand)
    return [xRand, yRand]


if __name__ == '__main__':
    knowGoal = True
    setStart = False
    badBots = False
    numBad = 0
    badRobotsList = []
    badRobotsIDs = []

    userInputValid = False
    #board size, no catch currently for non-ints, defaults to 5 if int entered is less than 5
    while not userInputValid:
        print("Please enter the board edge size(must be at least 5):")
        inputTry = int(input())
        #try:
        #    inputTry += 1
        #    xSize = inputTry
        #    ySize = inputTry
        #    userInputValid = True
        #except TypeError:
        #    #empty catch, this does nothing except cause the loop to happen again
        #    inputTry =+1
        if inputTry < 5:
            xSize = 5
            ySize = 5
        else:
            xSize = int(inputTry)
            ySize = int(inputTry)
        userInputValid = True

    #reset for next loop
    userInputValid = False

    #determine scenario, repeats if invalid chosen
    while not userInputValid:
        print("Please enter the scenario number, 1, 2, 3, or 4:")
        userInput = input()
        if userInput == "1":
            knowGoal = True
            setStart = True
            userInputValid = True
        elif userInput == "2":
            knowGoal = False
            setStart = True
            userInputValid = True
        elif userInput == "3":
            knowGoal = False
            userInputValid = True
        elif userInput == "4":
            knowGoal = False
            badBots = True
            userInputValid = True
        
    print("Beginning Scenario: "+ str(userInput) + "\n")

    #set goal location for #1
    if not knowGoal:
        #randomly chosen if not scenario 1
        goalX = random.randint(0,xSize-1)
        goalY = random.randint(0,ySize-1)
    else:
        #user chooses goal location
        print("Please give the goal X coordinate from 0 to "+str(xSize-1))
        goalX = int(input())
        print("Please give the goal Y coordinate from 0 to "+str(ySize-1))
        goalY = int(input())


    if(os.path.isfile("robotattack.log")):
        os.remove("robotattack.log");

    #xSize = 5
    #ySize = 5

    condition = threading.Condition()
    m = Map(xSize, ySize, goalX, goalY)

    #number of characters to shift in Caesar cipher, acts as key for "encryption"
    cipherDistance = 1

    #choose the number of robots, needs at least 2, no catch for invalid/non-int inputs
    print("Choose the number of robots:")
    numRobotsInput = int(input())
    if numRobotsInput < 2:
        numRobots = 2
    else:
        numRobots = numRobotsInput

    if(badBots):
        print("Please give the number of malicious robots: ")
        numBad = int(input())
        numRobots+=numBad

    rules = Rules(numRobots, m, condition)

    rules.start()

    robots = []
    robotIDs = []
    numGoodBots = numRobots-numBad
    for i in range(0,numGoodBots):
        uniqueIDfound = False
        
        while not uniqueIDfound:
            newID = random.randint(1, 99)
            if newID not in robotIDs:
                uniqueIDfound = True

        robotIDs.append(newID)
        #place robots on board if allowed
        if setStart:
            isFilled = True
            while isFilled:
                print("Robot "+str(newID) + " X starting location from 0 to "+str(xSize-1)+": ")
                robotX = int(input())
                print("Robot "+str(newID) + " Y starting location from 0 to "+str(xSize-1)+": ")
                robotY = int(input())
                isFilled = m.checkIfFilled(robotX, robotY)
                #print("propLoc" + str(propositionalLocation))
                if isFilled == True:
                    print("That location is already taken")
                location = []
                location.append(robotX)
                location.append(robotY)
        else:
            #random robot location
            location = checkRobotPlacement(m)
        r1 = Robot(location[0],location[1],xSize,ySize,m, newID, rules, condition, cipherDistance)
        badRobotsList.append(r1)
    
    if(badBots):

        for i in range(0,numBad):
            uniqueIDfound = False
        
            while not uniqueIDfound:
                newID = random.randint(1, 99)
                if newID not in robotIDs:
                    uniqueIDfound = True

            badRobotsIDs.append(newID)

            location = checkRobotPlacement(m)
            rBad1 = BadRobot(location[0],location[1],xSize,ySize,m, newID, rules, condition)
            badRobotsList.append(rBad1)


    if(badBots):
        print("Added malicious robots with IDs: "+str(badRobotsIDs))

    m.print()
    n = Network()

    if knowGoal:
        for r in robots:
            r.addGoal(m.goal)

    for r in robots:
        n.addRobots(r)

    for badR in badRobotsList:
        n.addRobots(badR)

    for r in robots:
        r.robotConnectToNetwork(n)

    for badR in badRobotsList:
        badR.robotConnectToNetwork(n)
    
    for r in robots:
        r.start()

    for badR in badRobotsList:
        badR.start()

    #t_rules.join()

    #m.print()
    #r1.move("r", m)
    #r2.move("d", m)
    #for i in m.mlist:
    #    i.getLatest(m.matrix)

    #r1.printKnowledge()
    #r1.printPos()
    #m.print()
    print("Set to wait 1 second between each round.")
    rules.join()
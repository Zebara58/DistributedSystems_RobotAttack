from threading import Thread
import threading
from Map import Map
from Robot import Robot
from Rules import Rules
from Network import Network
import os
import random
from cipher import *


#Robot/malicious in matrix is 1
#Empty spaces is 0
#Goal is 2

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

    userInputValid = False
    #board size, no catch currently for non-ints
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
        print(xSize)
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
        print("Please give the goal X coordinate from 0 to "+str(xSize-1))
        goalX = int(input())
        print("Please give the goal Y coordinate from 0 to "+str(ySize-1))
        goalY = int(input())




    #os.remove("robotattack.log");

    #xSize = 5
    #ySize = 5

    condition = threading.Condition()
    m = Map(xSize, ySize, goalX, goalY)

    #number of characters to shift in Caesar cipher, acts as key for "encryption"
    cipherDistance = 1

    #choose the number of robots
    print("Choose the number of robots:")
    numRobotsInput = int(input())
    if numRobotsInput < 2:
        numRobots = 2
    else:
        numRobots = numRobotsInput


    rules = Rules(numRobots, m, condition)
    print("before rules")
    rules.start()
    print("rules started")
    robots = []
    robotIDs = []
    for i in range(0,numRobots):
        uniqueIDfound = False
        
        while not uniqueIDfound:
            newID = random.randint(1, 99)
            if newID not in robotIDs:
                uniqueIDfound = True

        robotIDs.append(newID)
        #place robots on board if allowed
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
        location = checkRobotPlacement(m)
        r1 = Robot(location[0],location[1],xSize,ySize,m, newID, rules, condition, numRobots, cipherDistance)
        robots.append(r1)
    
    m.print()
    n = Network()

    if knowGoal:
        for r in robots:
            r.addGoal(m.goal)

    for r in robots:
        n.addRobots(r)

    for r in robots:
        r.robotConnectToNetwork(n)
    
    for r in robots:
        r.start()

    #t_rules.join()

    #m.print()
    #r1.move("r", m)
    #r2.move("d", m)
    #for i in m.mlist:
    #    i.getLatest(m.matrix)

    #r1.printKnowledge()
    #r1.printPos()
    #m.print()
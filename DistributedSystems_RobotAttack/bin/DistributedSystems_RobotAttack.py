from threading import Thread
import threading
from Map import Map
from Robot import Robot
from Rules import Rules
from Network import Network
import os
import random

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
    setStart = True
    badBots = False

    userInputValid = False

    while not userInputValid:
        print("Please enter the scenario number, 1, 2, or 3:")
        userInput = input()
        if userInput == "1":
            knowGoal = True
            userInputValid = True
        elif userInput == "2":
            knowGoal = False
            userInputValid = True
        elif userInput == "3":
            knowGoal = False
            userInputValid = True
        
    print("Beginning Scenario: "+ str(userInput) + "\n")




    os.remove("robotattack.log");

    xSize = 5
    ySize = 5

    condition = threading.Condition()
    m = Map(xSize, ySize)

    numRobots = 5
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
        location = checkRobotPlacement(m)
        r1 = Robot(location[0],location[1],xSize,ySize,m, newID, rules, condition, numRobots)
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
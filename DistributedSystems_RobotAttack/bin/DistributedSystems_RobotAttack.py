from threading import Thread
import threading
from Map import Map
from Robot import Robot
from Rules import Rules
from Network import Network
import os

#Robot/malicious in matrix is 1
#Empty spaces is 0
#Goal is 2

#Matrix[x][y]
import time
if __name__ == '__main__':

    os.remove("robotattack.log");

    xSize = 5
    ySize = 5

    condition = threading.Condition()
    m = Map(xSize, ySize)

    numRobots = 2
    rules = Rules(numRobots, m, condition)
    #print("before rules")
    rules.start()
    #condition.acquire()
    #condition.notify()
    #condition.release()
    #print("rules started")


    r1 = Robot(0,0,xSize,ySize,m, 1, rules, condition, 2)
    r2 = Robot(1,1,xSize,ySize,m, 2, rules, condition, 2)
    n = Network()
    n.addRobots(r1)
    n.addRobots(r2)
    r1.robotConnectToNetwork(n)
    r2.robotConnectToNetwork(n)
    
    #print("before robot")
    r1.start()
    #print("robot started")
    r2.start()

    #t_rules.join()

    #m.print()
    #r1.move("r", m)
    #r2.move("d", m)
    #for i in m.mlist:
    #    i.getLatest(m.matrix)

    #r1.printKnowledge()
    #r1.printPos()
    #m.print()
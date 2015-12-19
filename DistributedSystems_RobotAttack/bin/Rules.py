#Name: Kyle Brennan and Sean Kearney
#Date: 12/18/2015
#Class: CSCI 652
#Institution: Rochester Institute of Technology
#Description: This is the Rules thread that enforces turn order.

from threading import Thread
import threading
import logging
import time
class Rules(Thread):
    #Tells all if everyone took their turn

    #Pre: This takes the number of robots, the Map object pointer,
    #and the condition object for synchronization with the robots.
    def __init__(self, numR, m, cv):
        self.numR = numR
        self.notifyA = 0
        self.mainMap = m 
        self.cv = cv
        Thread.__init__(self)
        logging.basicConfig(filename='robotattack.log',level=logging.DEBUG)
        #logging.FileHandler(filename='robotattack.log', mode='w')

    #Post: Enforce turn order.
    def run(self):
        gameOver = False 
        logging.info("started!")
        logging.info("thread cv")
        while(not gameOver):
            if(self.notifyA==self.numR):
                #logging.info("notifyA limit reached!")

                #Wait one second between rounds
                time.sleep(1)

                self.notifyA=0
                with self.cv:
                    self.cv.acquire()
                    self.mainMap.print()
                    self.cv.notifyAll()
                    self.cv.release()
                #logging.info("notifyA limit reached OVER!")
        logging.info('rules finished!');

   
    def inc(self):
        self.notifyA +=1
        #print("notifyA inc")
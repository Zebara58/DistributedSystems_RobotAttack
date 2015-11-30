from threading import Thread
import threading
import logging
class Rules(Thread):
    #Tells all if everyone took their turn
    def __init__(self, numR, m, cv):
        self.numR = numR
        self.notifyA = 0
        self.mainMap = m 
        self.cv = cv
        Thread.__init__(self)
        #logging.basicConfig(filename='robotattack.log',level=logging.DEBUG)
        logging.FileHandler(filename='robotattack.log', mode='w')

    def run(self):
        gameOver = False 
        logging.info("started!")
        with self.cv:
            logging.info("thread cv")
            while(not gameOver):
                if(self.notifyA==self.numR):
                    logging.info("notifyA limit reached!")
                    self.notifyA=0
                    cv.notifyAll()
                    self.mainMap.print()
        logging.info('rules finished!');

   
    def inc(self):
        self.notifyA +=1
        print("notifyA inc")
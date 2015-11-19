from threading import Thread
import threading
class Rules:
    #Tells all if everyone took their turn
    def __init__(self, numR, m):
        self.numR = numR
        self.notifyA = 0
        self.mainMap = m 

    def operate(self, cv):
        gameOver = False 
        with cv:
            while(not gameOver):
                if(self.notifyA==self.numR):
                    print("notifyA limit reached!")
                    self.notifyA=0
                    cv.notifyAll()
                    self.mainMap.print()

   
    def inc(self):
        self.notifyA +=1
        print("notifyA inc")
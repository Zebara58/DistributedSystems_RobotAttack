#Name: Kyle Brennan and Sean Kearney
#Date: 12/18/2015
#Class: CSCI 652
#Institution: Rochester Institute of Technology
#Description: This is the Network object that robots use to broadcast 
#messages to all other robots. 

from threading import Thread
import threading
import logging
class Network(Thread):
    def __init__(self):
        self.robotList = []

    def addRobots(self, robot):
        self.robotList.append(robot)

    #Pre: This takes any array with the requirement that the first element is the 
    #robot ID who sent the request.
    #Post: This sends the messages to all other robots besides the sender.
    def broadcastMessage(self, message):
        #logging.info("broadcast starting!")
        for i in self.robotList:
            if i.robotID != message[0]:
                #send to robot
                #logging.info("sent to -> "+str(i.robotID))
                i.recieveMessage(message)

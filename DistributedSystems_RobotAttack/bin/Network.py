from threading import Thread
import threading
import logging
class Network(Thread):
    def __init__(self):
        self.robotList = []

    def addRobots(self, robot):
        self.robotList.append(robot)

    def broadcastMessage(self, message):
        logging.info("broadcast starting!")
        for i in self.robotList:
            if i.robotID != message[0]:
                #send to robot
                logging.info("sent to -> "+str(i.robotID))
                i.recieveMessage(message)

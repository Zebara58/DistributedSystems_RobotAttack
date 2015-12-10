from threading import Thread
import threading
class Network(Thread):
    def __init__(self):
        self.robotList = []

    def addRobots(self, robot):
        self.robotList.append(robot)

    def broadcastMessage(self, message):
        for i in self.robotList:
            if i.robotID != message[0]:
                #send to robot
                i.recieveMessage(message)

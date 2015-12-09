class Network(Thread):
    def __init__(self):
        self.robotList = []

    def addRobots(self, robot):
        self.robotList.append(robot)

    def sendMessageBroadcast(self, message):
        for i in robotList:
            if i.robotID != message[0]:
                

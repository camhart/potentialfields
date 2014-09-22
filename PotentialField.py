import math

class PotentialField:

    def calculateField(self, x, y):
        raise NotImplemented("not implemented")

class FlagField(PotentialField):

    def __init__(self, goalX, goalY):
        self.goalX = goalX
        self.goalY = goalY
        self.alpha = 15.0

    def setGoal(self, x, y):
        '''
        Sets new goal (flag) coordinate
        '''
        self.goalX = x
        self.goalY = y

    def calculateField(self, x, y):
        diffX = x - self.goalX
        diffY = y - self.goalY
        dist = math.sqrt(math.pow(diffX, 2) + math.pow(diffY, 2))
        theta = math.atan2(diffY, diffX)

        retX = 0
        retY = 0

        retX = self.alpha * math.cos(theta)
        retY = self.alpha * math.sin(theta)
#         if(dist > 5):
#             retX = self.alpha * math.cos(theta)
#             retY = self.alpha * math.sin(theta)
#         else:
#             retX = self.alpha * (dist/5) * math.cos(theta)
#             retY = self.alpha * (dist/5) * math.sin(theta)

        return (retX, retY)
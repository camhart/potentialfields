import math

class PotentialField(object):

    def calculateField(self, x, y):
        raise NotImplemented("not implemented")

class GoalField(PotentialField):
    '''
        GoalField (attraction field), useful for getting Flags and returning Flags
    '''

    def __init__(self, goalX, goalY):
        self.avoidX = goalX
        self.avoidY = goalY
        self.alpha = -10.0       #negative pull's in

    def setGoal(self, x, y):
        '''
        Sets new goal (flag) coordinate
        '''
        self.avoidX = x
        self.avoidY = y

    def calculateField(self, x, y):
        diffX = x - self.avoidX
        diffY = y - self.avoidY
        if diffX == 0 and diffY == 0: #sitting on the goal
            return (0, 0)

        dist = math.sqrt(math.pow(diffX, 2) + math.pow(diffY, 2))
        theta = math.atan2(diffY, diffX)

        retX = self.alpha * math.cos(theta)
        retY = self.alpha * math.sin(theta)

        return (retX, retY)

class RepulsionField(PotentialField):
    '''
        GoalField (attraction field), useful for getting Flags and returning Flags
    '''

    def __init__(self, avoidX, avoidY):
        self.avoidX = avoidX
        self.avoidY = avoidY
        self.alpha = 15
        self.range = 25

    def setAvoid(self, x, y):
        '''
        Sets new goal (flag) coordinate
        '''
        self.avoidX = x
        self.avoidY = y

    def calculateField(self, x, y):
        diffX = x - self.avoidX
        diffY = y - self.avoidY

        dist = math.sqrt(math.pow(diffX, 2) + math.pow(diffY, 2))

        if dist < self.range:
            s = 1.0

            if dist < self.range / 4:
                s = 2.0
            elif dist < self.range / 2:
                s = 1.5

            theta = math.atan2(diffY, diffX)

            retX = self.alpha * s * math.cos(theta)
            retY = self.alpha * s * math.sin(theta)

            return (retX, retY)
        return (0, 0)

class TangentField(PotentialField):

    def __init__(self, cx, cy, r):
        self.x = cx
        self.y = cy
        self.range = r
        self.alpha = -20.0
        self.rotation = +90.0

    def calculateField(self, x, y):
        diffX = x - self.x
        diffY = y - self.y

        dist = math.sqrt(math.pow(diffX, 2) + math.pow(diffY, 2))

        if dist < self.range:
            theta = math.atan2(diffY, diffX)

            retX = self.alpha * math.cos(theta + self.rotation)
            retY = self.alpha * math.sin(theta + self.rotation)

            return (retX, retY)
        return (0, 0)

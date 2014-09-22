import math
from .PotentialField import TangentField

class Obstacle(TangentField):

    def __init__(self, points):
        self.alpha = -20.0
        self.rotation = +90.0
        self.x = 0  #center x
        self.y = 0  #center y
        self.range = 0 #range
        for point in points:
            px, py = point
            self.x += px
            self.y += py

        self.x = self.x / float(len(points))
        self.y = self.y / float(len(points))

        for point in points:
            px, py = point
            dist = math.sqrt(math.pow(self.x - px, 2) + math.pow(self.y - py, 2))
            if dist > self.range:
                self.range = dist
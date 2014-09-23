import math
from potentialfields.fields import TangentField

class Obstacle(TangentField):

    def __init__(self, points):
        self.alpha = -20.0
        self.rotation = +90.0
        self.x = 0  #center x
        self.y = 0  #center y
        self.range = 0 #range
        for point in points:
            px, py = point
            self.x += float(px)
            self.y += float(py)

        self.x = self.x / float(len(points))
        self.y = self.y / float(len(points))

        for point in points:
            px, py = point
            px = float(px)
            py = float(py)
            dist = math.sqrt(math.pow(self.x - px, 2) + math.pow(self.y - py, 2))
            if dist > self.range:
                self.range = dist

        def getKey(self):
            return "Obstacle %d, %d" % (self.x, self.y)

        def toString(self):
            return unicode(self)

        def __unicode__(self):
            return "Obstacle: (%f, %f), range: %f, alpha: %f, rotation: %f" % \
                (self.x, self.y, self.range, self.alpha, self.rotation)

        def __str__(self):
            return unicode(self).encode('utf-8')

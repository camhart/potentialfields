class Fields(object):
    '''
        Object containing all fields
    '''

    def __init__(self):
        self.fields = {}

    def setGoalAll(self, x, y):
        '''
        Sets new goal (flag) coordinate for all fields with setAvoid
        '''
        for field in self.fields.values():
            if field.setGoal:
                field.setGoal(x, y)

    def setGoal(self, key, x, y):
        self.fields[key].setGoal(x, y)

    def setAvoid(self, key, x, y):
        self.fields[key].setAvoid(x, y)

#     def setAvoidAll(self, x, y):
#         '''
#         Sets new goal (flag) coordinate for all fields with setAvoid
#         '''
#         for field in self.fields.values():
#             if field.setAvoid:
#                 field.setAvoid(x, y)

    def addField(self, key, field):
        '''
        Adds field to list of fields.  Replaces if key already exists.
        '''
        if self.fields.has_key(key):
            self.fields.pop(key)
        self.fields[key] = field

    def calculateField(self, x, y):
        '''
        Calculates the field for the position x, y using all fields
            added using addField
         return tuple (deltaX, deltaY)
        '''

        deltaX = 0
        deltaY = 0
        for field in self.fields.values():
            (fx, fy) = field.calculateField(x, y)
            deltaX += fx
            deltaY += fy
        return (deltaX, deltaY)
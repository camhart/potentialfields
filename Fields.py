class Fields:
    '''
        Object containing all fields
    '''

    def __init__(self):
        self.fields = []

    def setGoal(self, x, y):
        '''
        Sets new goal (flag) coordinate for all fields with setGoal
        '''
        for field in self.fields:
            if field.setGoal:
                field.setGoal(x, y)

    def addField(self, field):
        '''
        Adds field to list of fields
        '''
        self.fields.append(field)

    def calculateField(self, x, y):
        '''
        Calculates the field for the position x, y using all fields
            added using addField
         return tuple (deltaX, deltaY)
        '''

        deltaX = 0
        deltaY = 0
        for field in self.fields:
            (x, y) = field.calculateField(x, y)
            deltaX += x
            deltaY += y
        return (deltaX, deltaY)
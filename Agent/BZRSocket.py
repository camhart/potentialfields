
import socket
import argparse
import time
import math
import cmath
import bzrplot
# import PotentialFields.Obstacle.Obstacle
from PotentialFields.Fields import Fields
from PotentialFields.PotentialField import GoalField
from PotentialFields.Obstacle import Obstacle


class BZRTank(object):
	def __init__(self, socket, index):
		self.socket = socket
		self.index = index

		self.status = "alive"
		self.shotsAvailable = 0
		self.timeToReload = 0
		self.position = complex(0, 0)
		self.heading = 0
		self.direction = cmath.rect(1.0, self.heading)
		self.velocity = complex(0, 0)
		self.angularVelocity = 0

		self.targetDirection = complex(0, 0)

	def Update(self, responseLine):
		self.UpdateParameters(responseLine)
		self.UpdateLogic()

	def UpdateParameters(self, responseLine):
		if responseLine.response != "mytank":
			raise Exception("Expected mytank got " + responseLine.response)
		self.status = responseLine.parameters[2]
		self.shotsAvailable = int(responseLine.parameters[3])
		self.timeToReload = float(responseLine.parameters[4])
		self.position = complex(float(responseLine.parameters[6]), float(responseLine.parameters[7]))
		self.heading = float(responseLine.parameters[8])
		self.velocity = complex(float(responseLine.parameters[9]), float(responseLine.parameters[10]))
		self.angularVelocity = float(responseLine.parameters[11])

		self.direction = cmath.rect(1.0, self.heading)

	def Shoot(self):
		return self.socket.IssueCommand("shoot " + str(self.index), True)[0].response != "fail"

	def SetSpeed(self, value):
		self.socket.IssueCommand("speed " + str(self.index) + " " + str(value))

	def SetAngularVelocity(self, value):
		self.SendAngularVelocity(value)
		self.targetDirection = complex(0, 0)

	def SendAngularVelocity(self, value):
		self.socket.IssueCommand("angvel " + str(self.index) + " " + str(value))

	def RotateTowards(self, direction):
		self.targetDirection = direction

	def UpdateLogic(self):
		if self.targetDirection != complex(0, 0):
			targetAngluarVelocity = cmath.phase(self.direction.conjugate() * self.targetDirection)
			self.SendAngularVelocity(targetAngluarVelocity)



class BZRTankGroup(object):
	def __init__(self, socket):
		self.socket = socket
		self.tanks = []

		tankList = socket.IssueCommand("mytanks")

		index = 0
		for tankResponse in tankList:
			if index != int(tankResponse.parameters[0]):
				raise Exception("Mismatched index")

			tank = BZRTank(socket, index)
			tank.UpdateParameters(tankResponse)
			self.tanks.append(tank)
			index = index + 1

	def Update(self):
		tankList = self.socket.IssueCommand("mytanks")
		for tankResponse in tankList:
			self.tanks[int(tankResponse.parameters[0])].Update(tankResponse)

	def __getitem__(self, index):
		return self.tanks[index]

class BZRGame(object):
	def __init__(self, socket):
		self.socket = socket
		self.obstacles = []
		self.points = []
		self.fields = Fields()
		self.mycolor = None

		#Build Obstacles
		self.BuildConstants()
		self.BuildObstacles()

		print self.mycolor
# 		for ob in self.obstacles:
# 			print "Obstacle: (%f, %f), range: %f, alpha: %f, rotation: %f" % \
#                 (ob.x, ob.y, ob.range, ob.alpha, ob.rotation)

# 		print([str(obstacle) for obstacle in self.obstacles])

	def BuildObstacles(self):
		obstacleResponse = self.socket.IssueCommand("obstacles")

		for rl in obstacleResponse:
			x = -1
			y = -1
			points = []
			for param in rl.parameters:
				if(x == -1):
					x = float(param)
				elif(y == -1):
					y = float(param)
					points.append((x, y))
					x = -1
					y = -1

			obstacle = Obstacle(points)
# 			print getattr(Obstacle, 'getKey')
			self.fields.addField("Obstacle (%d, %d)" % (obstacle.x, obstacle.y), obstacle)
			self.obstacles.append(obstacle)
			self.points.append(points)
			points = []

		return self.obstacles

	def BuildConstants(self):
		constants = self.socket.IssueCommand("constants")

		for i in xrange(len(constants)):
			if(i == 0):
				self.mycolor = constants[i].parameters[1]
				break


	def UpdateFlags(self):
		baseResponse = self.socket.IssueCommand("flags")

		for br in baseResponse:
			print br.parameters
			if br.parameters[1] == 'none' and br.parameters[0] != self.mycolor:
				self.fields.addField(br.parameters[0], GoalField(float(br.parameters[2]), float(br.parameters[3])))
				break	#might want to change this to let them go after different flags...

class BZRResponseLine(object):
	def __init__(self, line):
		parameters = line.split()
		self.response = parameters[0]
		self.parameters = parameters[1:]

class BZRSocket(object):
	def __init__(self, host, port):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect( (host, port) )
		self.pendingData = ""

		serverHandshake = self.ReadLine()

		if serverHandshake != "bzrobots 1":
			raise Exception("Invalid handshake from server")

		self.socket.send("agent 1\n")

		self.mytanks = BZRTankGroup(self)

	def ReadLine(self):
		endLineLocation = self.pendingData.find("\n")
		while endLineLocation == -1:
			newData = self.socket.recv(1024)

			if newData == "":
				raise Exception("Socket closed")
			else:
				self.pendingData += newData

			endLineLocation = self.pendingData.find("\n")

		result = self.pendingData[0:endLineLocation]
		self.pendingData = self.pendingData[endLineLocation+1:]

		return result

	def IssueCommand(self, commandMessage, silentFail = False):
		self.socket.send(commandMessage + "\n")

		result = self.ReadResponse()

		if result[0].response == "fail" and not silentFail:
			raise Exception("Failed to issue command: " + commandMessage + " response: " + " ".join(result[0].parameters))

		return result

	def ReadResponse(self):
		ack = self.ReadLine()

		if ack[0:3] != "ack":
			raise Exception("Invalid server response")

		responseLines = []

		line = self.ReadLine()

		if line == "begin":
			line = self.ReadLine()
			while line != "end":
				responseLines.append(BZRResponseLine(line))
				line = self.ReadLine()
		else:
			responseLines.append(BZRResponseLine(line))

		return responseLines


if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog="BZRSocket")
	parser.add_argument("--host", help="the host to connect to")
	parser.add_argument("--port", type=int, help="the port to connect to")
	args = parser.parse_args()

	socketTest = BZRSocket(args.host, args.port)

	game = BZRGame(socketTest)
	game.UpdateFlags()

	bzrplot.Temp.allFields = game.fields

	bzrplot.plot_single(bzrplot.fields, game.points, 'game.png')

	tankTest = socketTest.mytanks[1]
	tankTest.SetSpeed(1.0)
	tankTest.RotateTowards(complex(1, 1))

	while True:
		socketTest.mytanks.Update()


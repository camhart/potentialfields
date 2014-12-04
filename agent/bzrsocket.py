
import socket
import argparse
import time
import math
import cmath
import bzrplot
import kalman

# import potentialfields.ObstacleField.ObstacleField
from potentialfields.fieldmanager import FieldManager
from potentialfields.fields import GoalField, ShotField, ObstacleField, TankField
from potentialfields.fieldmanager import FieldManager

class BZROccGrid(object):
	def __init__(self, x, y, data):
		self.x = x
		self.y = y
		self.width = len(data)
		self.height = len(data[0])
		self.data = data

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

	def update(self, responseLine):
		self.updateParameters(responseLine)
		self.updateLogic()

	def updateParameters(self, responseLine):
		if responseLine.response != "mytank":
			raise Exception("Expected mytank got " + responseLine.response)
		self.status = responseLine.parameters[2]
		self.shotsAvailable = int(responseLine.parameters[3])
		self.timeToReload = float(responseLine.parameters[4])
		self.flag = responseLine.parameters[5]
		self.position = complex(float(responseLine.parameters[6]), float(responseLine.parameters[7]))
		self.heading = float(responseLine.parameters[8])
		self.velocity = complex(float(responseLine.parameters[9]), float(responseLine.parameters[10]))
		self.angularVelocity = float(responseLine.parameters[11])

		self.direction = cmath.rect(1.0, self.heading)

	def shoot(self):
		return self.socket.issueCommand("shoot " + str(self.index), True)[0].response != "fail"

	def setSpeed(self, value):
		self.socket.issueCommand("speed " + str(self.index) + " " + str(value))

	def setAngularVelocity(self, value):
		self.sendAngularVelocity(value)
		self.targetDirection = complex(0, 0)

	def sendAngularVelocity(self, value):
		self.socket.issueCommand("angvel " + str(self.index) + " " + str(value))

	def rotateTowards(self, direction):
		self.targetDirection = direction

	def updateLogic(self):
		if self.targetDirection != complex(0, 0):
			targetAngluarVelocity = cmath.phase(self.direction.conjugate() * self.targetDirection)
			self.sendAngularVelocity(targetAngluarVelocity)

	def sampleGrid(self):
		gridResponse = self.socket.issueCommand("occgrid " + str(self.index), True)

		if len(gridResponse) == 0 or gridResponse[0].response == "fail":
			return None

		position = gridResponse[0].parameters[0].split(",")
		size = gridResponse[1].parameters[0].split("x")

		data = []

		for x in range(int(size[0])):
			row = []

			for y in range(int(size[1])):
				row.append(float(gridResponse[x + 2].response[y]))

			data.append(row)

		return BZROccGrid(int(position[0]), int(position[1]), data)
			


class BZRTankGroup(object):
	def __init__(self, socket):
		self.socket = socket
		self.tanks = []

		tankList = socket.issueCommand("mytanks")

		index = 0
		for tankResponse in tankList:
			if index != int(tankResponse.parameters[0]):
				raise Exception("Mismatched index")

			tank = BZRTank(socket, index)
			tank.updateParameters(tankResponse)
			self.tanks.append(tank)
			index = index + 1

	def update(self):
		tankList = self.socket.issueCommand("mytanks")
		for tankResponse in tankList:
			self.tanks[int(tankResponse.parameters[0])].update(tankResponse)

	def __getitem__(self, index):
		return self.tanks[index]

class BZREnemyTank(object):
	def __init__(self):
		self.status = None
		self.flag = None
		self.position = complex(0, 0)
		self.angle = 0
		self.kalmanFilter = kalman.Filter()
		self.lastTime = time.clock()
		self.wasDead = True

	def updateParameters(self, responseLine):
		self.status = responseLine.parameters[2]
		self.flag = responseLine.parameters[3]
		self.position = complex(float(responseLine.parameters[4]), float(responseLine.parameters[5]))
		self.angle = responseLine.parameters[6]

		isDead = self.status == "dead"

		if self.wasDead and not isDead:
			self.kalmanFilter.ResetPosition(self.position.real, self.position.imag)
			self.lastTime = time.clock()
		else:
			thisTime = time.clock()
			self.kalmanFilter.AddSample(self.position.real, self.position.imag, thisTime - self.lastTime)
			self.lastTime = thisTime

		self.wasDead = isDead

class BZRTeam(object):
	def __init__(self):
		self.color = None
		self.flagPosition = complex(0, 0)
		self.tanks = {}
		self.basePosition = complex(0, 0)
		self.flagCarriedBy = None


class BZRGame(object):
	def __init__(self, socket):
		self.socket = socket
		self.obstacles = []
		self.points = []
		self.fields = FieldManager()
		self.mycolor = None
		self.worldSize = 0

		self.truePositive = 0
		self.trueNegative = 0
	
		self.otherConstants = {}

		self.teams = {}
		# 'color' : BZRTeam object

		#Build Obstacles
		self.buildTeams()
		self.buildConstants()
		self.buildObstacles()

	def willHitEnemy(self, fireingTank):

		for color in self.teams:
			if color != self.mycolor:
				team = self.teams[color]
				for tankid in team.tanks:
					enemyTank = team.tanks[tankid]
					if self.willHitTarget(fireingTank, enemyTank.kalmanFilter):
						return True

		return False

	def willHitTarget(self, fireingTank, targetKalmanFilter):
		return targetKalmanFilter.WillProjectileHit(
			fireingTank.position.real, fireingTank.position.imag,
			fireingTank.direction.real * self.shotSpeed, fireingTank.direction.imag * self.shotSpeed, 
			self.tankRadius, self.shotLifetime)

	def buildObstacles(self):
		obstacleResponse = self.socket.issueCommand("obstacles", True)

		if obstacleResponse[0].response == "fail":
			return []

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

			obstacle = ObstacleField(points)

			self.fields.addField("ObstacleField (%d, %d)" % (obstacle.x, obstacle.y), obstacle)
			self.obstacles.append(obstacle)
			self.points.append(points)
			points = []

		return self.obstacles

	def buildTeams(self):
		teamsResponse = self.socket.issueCommand("bases")

		for res in teamsResponse:
			team = BZRTeam()
			team.color = res.parameters[0]
			team.basePosition = complex(float(res.parameters[1]), float(res.parameters[2]))
			self.teams[team.color] = team

		otherTankResponse = self.socket.issueCommand("othertanks")
		for res in otherTankResponse:
			team = self.teams[res.parameters[1]]
			team.tanks[res.parameters[0]] = BZREnemyTank()
			team.tanks[res.parameters[0]].updateParameters(res)

		self.enemyTeamColors = self.teams.keys()
			

	def updateTeams(self):
		flagsResponse = self.socket.issueCommand("flags")


		for res in flagsResponse:
			#color, possesing, positionx, positiony
			team = self.teams[res.parameters[0]]
			team.flagPosition = complex(float(res.parameters[2]), float(res.parameters[3]))
			team.flagCarriedBy = res.parameters[1]

		otherTankResponse = self.socket.issueCommand("othertanks")
		
		for res in otherTankResponse:
			team = self.teams[res.parameters[1]]
			tank = team.tanks[res.parameters[0]]
			tank.updateParameters(res)
			tankField = TankField(tank.position.real, tank.position.imag)
			self.fields.addField("enemy_tank_%s" % (res.parameters[0]), tankField)

	def buildConstants(self):
		constants = self.socket.issueCommand("constants")

		for i in xrange(len(constants)):
			constantName = constants[i].parameters[0]
			if(constantName == "team"):
				self.mycolor = constants[i].parameters[1]
			elif constantName == "worldsize":
				self.worldSize = int(constants[i].parameters[1])
			elif constantName == "truepositive":
				self.truePositive = float(constants[i].parameters[1])
			elif constantName == "truenegative":
				self.trueNegative = float(constants[i].parameters[1])
			else:
				self.otherConstants[constantName] = constants[i].parameters[1]

		self.shotSpeed = float(self.otherConstants["shotspeed"])
		self.shotLifetime = float(self.otherConstants["shotrange"]) / self.shotSpeed
		self.tankRadius = float(self.otherConstants["tankradius"])

		self.enemyTeamColors.remove(self.mycolor)

	def update(self):
		self.updateShots()
		self.updateTeams()

	def updateShots(self):
		#shot 242.490422334 77.1400313101 78.5985078261 61.8245466422
		#shot x y origin_x origin_y
		shotResponse = self.socket.issueCommand("shots")

		#remove all shots fields
		self.fields.removeShotFields()

		shotNum = 0
		for shot in shotResponse:
			if shot.response == 'shot':
				shotField = ShotField(float(shot.parameters[0]), float(shot.parameters[1]))
				self.fields.addField("shot_%d" % (shotNum, ), shotField)
				shotNum+=1


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

		serverHandshake = self.readLine()

		if serverHandshake != "bzrobots 1":
			raise Exception("Invalid handshake from server")

		self.socket.send("agent 1\n")

		self.mytanks = BZRTankGroup(self)

	def readLine(self):
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

	def issueCommand(self, commandMessage, silentFail = False):
		self.socket.send(commandMessage + "\n")

		result = self.readResponse()

		if len(result) > 0 and result[0].response == "fail" and not silentFail:
			raise Exception("Failed to issue command: " + commandMessage + " response: " + " ".join(result[0].parameters))

		return result

	def readResponse(self):
		ack = self.readLine()

		if ack[0:3] != "ack":
			return [BZRResponseLine("fail")]

		responseLines = []

		line = self.readLine()

		if line == "begin":
			line = self.readLine()
			while line != "end":
				responseLines.append(BZRResponseLine(line))
				line = self.readLine()
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

	bzrplot.Temp.allFields = game.fields

	bzrplot.plot_single(bzrplot.fields, game.points, 'game.png')

	tankTest = socketTest.mytanks[1]
	tankTest.setSpeed(1.0)
	tankTest.rotateTowards(complex(1, 1))

	while True:
		socketTest.mytanks.update()


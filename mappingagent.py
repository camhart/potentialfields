
from agent.bzrsocket import BZRSocket, BZRGame
from potentialfields.fields import GoalField
from potentialfields.fieldmanager import FieldManager
import argparse
import time
import math
import cmath
import random
import bzrplot

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from numpy import zeros

class ObstacleData(object):
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.data = zeros((height, width, 3))
		self.mapped = zeros((height, width))

		self.gridSize = 25

		for y in range(height):
			for x in range(width):
				self.data[y][x][0] = 0.25

	def setSample(self, x, y, value):
		if x >= 0 and x < self.width and y >= 0 and y < self.width:		
			self.mapped[y][x] = 1
			self.data[y][x][0] = 0
			self.data[y][x][1] = value * 0.75 + 0.25
			self.data[y][x][2] = value
		

	def setOccSample(self, occSample):
		self.gridSize = int(occSample.width / 4)

		for x in range(occSample.width):
			for y in range(occSample.height):
				targetX = x + occSample.x + self.width / 2
				targetY = y + occSample.y + self.height / 2
				self.setSample(targetX, targetY, occSample.data[x][y])

	def isCharted(self, x, y):
		return self.mapped[int(y) + self.width / 2, int(x) + self.height / 2] == 1
		
	def getUnchartedPoint(self, startX, startY):

		gridStepX = self.width / self.gridSize
		gridStepY = self.height / self.gridSize

		gridOffsetX = int(startX - self.gridSize / 2) / self.gridSize
		gridOffsetY = int(startY - self.gridSize / 2) / self.gridSize

		#rough check
		for y in xrange(gridStepY):
			for x in xrange(gridStepX):
				xPoint = self.gridSize * ((x + gridOffsetX) % gridStepX)
				yPoint = self.gridSize * ((y + gridOffsetY) % gridStepY)

				if self.mapped[yPoint, xPoint] != 1:
					return xPoint - self.width / 2, yPoint - self.height / 2

		#per pixel check
		for y in xrange(self.height):
			for x in xrange(self.width):
				if self.mapped[x, y] != 1:
					return x - self.width / 2, y - self.height / 2

		return None

def DrawObstacleData(data):
	# This assumes you are using a numpy array for your grid
	glRasterPos2f(-1, -1)
	glDrawPixels(data.width, data.height, GL_RGB, GL_FLOAT, data.data)
	glFlush()
	glutSwapBuffers()

def InitDebugWindow(width, height):
	global window
	glutInit(())
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
	glutInitWindowSize(width, height)
	glutInitWindowPosition(0, 0)
	window = glutCreateWindow("Grid filter")
	glutDisplayFunc(DrawObstacleData)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

class FieldFollowTank(object):
	def __init__(self, bzrTank, field):
		self.bzrTank = bzrTank
		self.field = field

	def update(self):
		fieldX, fieldY = self.field.calculateField(self.bzrTank.position.real, self.bzrTank.position.imag)
		fieldDir = complex(fieldX, fieldY)

		if fieldDir != complex(0, 0):
			fieldDirUnit = fieldDir / abs(fieldDir)

			self.bzrTank.setSpeed(max(0, (fieldDirUnit.conjugate() * self.bzrTank.direction).real))
			self.bzrTank.rotateTowards(fieldDirUnit)

		if self.bzrTank.shotsAvailable > 0:
			self.bzrTank.shoot()

class GridMappingTank(FieldFollowTank):
	def __init__(self, bzrTank, game, color, obstacleData):
		self.field = FieldManager()
		self.field.addField("world", game.fields)
		self.targetPoint = obstacleData.getUnchartedPoint(bzrTank.position.real, bzrTank.position.imag)
		self.goalField = GoalField(self.targetPoint[0], self.targetPoint[1])
		self.field.addField("flag", self.goalField)

		super(GridMappingTank,self).__init__(bzrTank, self.field)
		self.game = game
		self.targetColor = color
		self.obstacleData = obstacleData


	def update(self):
		gridSample = self.bzrTank.sampleGrid()

		if gridSample != None:
			self.obstacleData.setOccSample(gridSample)

		if self.targetPoint != None and self.obstacleData.isCharted(self.targetPoint[0], self.targetPoint[1]):
			self.targetPoint = self.obstacleData.getUnchartedPoint(self.bzrTank.position.real, self.bzrTank.position.imag)

			if self.targetPoint != None:
				self.goalField.x = self.targetPoint[0]
				self.goalField.y = self.targetPoint[1]

		super(GridMappingTank,self).update()

class SimpleAgent:
	def __init__(self, hostname, port):

		self.socket = BZRSocket(hostname, port)
		self.game = BZRGame(self.socket)

		InitDebugWindow(self.game.worldSize, self.game.worldSize)
		self.obstacleData = ObstacleData(self.game.worldSize, self.game.worldSize)

		index = 0
		self.tanks = []
		for tank in self.socket.mytanks.tanks:
			targetColor = self.game.enemyTeamColors[index % len(self.game.enemyTeamColors)]
			self.tanks.append(GridMappingTank(tank, self.game, targetColor, self.obstacleData))
			index = index + 1


	def run(self):
		lastPrint = time.time()
		imageCount = 0
		doPrint = False
		while True:
			self.socket.mytanks.update()
			self.game.update()

			for tank in self.tanks:
				tank.update()

			if(doPrint and time.time() - lastPrint > 5):
				bzrplot.plot(self.tanks[0].field, "curgame_%d.png" % (imageCount, ))
				imageCount+=1
				lastPrint = time.time()

			DrawObstacleData(self.obstacleData)

			time.sleep(0)


if __name__ == "__main__":


	parser = argparse.ArgumentParser(prog="potentialfieldagent")
	parser.add_argument("--host", help="the host to connect to")
	parser.add_argument("--port", type=int, help="the port to connect to")
	args = parser.parse_args()

	if args.host == None or args.port == None:
		parser.print_help()
	else:
		simpleAgent = SimpleAgent(args.host, args.port)
		simpleAgent.run()

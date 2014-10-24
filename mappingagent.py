
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
		self.data = zeros((width, height))

	def setOccSample(self, occSample):
		for x in range(occSample.width):
			for y in range(occSample.height):
				targetY = x + occSample.x + self.width / 2
				targetX = y + occSample.y + self.height / 2
				if targetX >= 0 and targetX < self.width and targetY >= 0 and targetY < self.width:
					self.data[targetX][targetY] = occSample.data[x][y]
		

def DrawObstacleData(data):
	# This assumes you are using a numpy array for your grid
	width, height = data.data.shape
	glRasterPos2f(-1, -1)
	glDrawPixels(width, height, GL_LUMINANCE, GL_FLOAT, data.data)
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
		flagPos = game.teams[color].flagPosition
		self.goalField = GoalField(flagPos.real, flagPos.imag)
		self.field.addField("flag", self.goalField)

		super(GridMappingTank,self).__init__(bzrTank, self.field)
		self.game = game
		self.targetColor = color
		self.obstacleData = obstacleData


	def update(self):
		if self.bzrTank.flag == '-':
			flagPos = self.game.teams[self.targetColor].flagPosition
			self.goalField.x = flagPos.real
			self.goalField.y = flagPos.imag
		else:
			homePos = self.game.teams[self.game.mycolor].basePosition
			self.goalField.x = homePos.real
			self.goalField.y = homePos.imag

		super(GridMappingTank,self).update()

		gridSample = self.bzrTank.sampleGrid()

		if gridSample != None:
			self.obstacleData.setOccSample(gridSample)

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

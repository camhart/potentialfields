
from agent.bzrsocket import BZRSocket, BZRGame
from potentialfields.fields import GoalField
from potentialfields.fieldmanager import FieldManager
import argparse
import time
import cmath
import random

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

class CaptureFlagTank(FieldFollowTank):
	def __init__(self, bzrTank, game, color):
		self.field = FieldManager()
		self.field.addField("world", game.fields)
		flagPos = game.teams[color].flagPosition
		self.goalField = GoalField(flagPos.real, flagPos.imag)
		self.field.addField("flag", self.goalField)

		super(CaptureFlagTank,self).__init__(bzrTank, self.field)
		self.game = game
		self.targetColor = color


	def update(self):
		if self.bzrTank.flag == '-':
			flagPos = self.game.teams[self.targetColor].flagPosition
			self.goalField.x = flagPos.real
			self.goalField.y = flagPos.imag
		else:
			homePos = self.game.teams[self.game.mycolor].basePosition
			self.goalField.x = homePos.real
			self.goalField.y = homePos.imag

		super(CaptureFlagTank,self).update()

class SimpleAgent:
	def __init__(self, hostname, port):

		self.socket = BZRSocket(hostname, port)
		self.game = BZRGame(self.socket)

		self.tanks = [CaptureFlagTank(self.socket.mytanks[0], self.game, "red"), CaptureFlagTank(self.socket.mytanks[1], self.game, "purple")]


	def run(self):
		while True:
			self.socket.mytanks.update()
			self.game.update()

			for tank in self.tanks:
				tank.update()

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

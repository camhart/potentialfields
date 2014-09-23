
from Agent import BZRSocket
from PotentialFields import PotentialField
from PotentialFields.Fields import Fields
from PotentialFields.Obstacle import Obstacle
import argparse
import time
import cmath
import random

class FieldFollowTank:
	def __init__(self, bzrTank, field):
		self.bzrTank = bzrTank
		self.field = field

	def update(self):
		fieldX, fieldY = self.field.calculateField(self.bzrTank.position.real, self.bzrTank.position.imag)
		fieldDir = complex(fieldX, fieldY)

		if fieldDir != complex(0, 0):
			fieldDirUnit = fieldDir / abs(fieldDir)

			self.bzrTank.SetSpeed(max(0, (fieldDirUnit.conjugate() * self.bzrTank.direction).real))
			self.bzrTank.RotateTowards(fieldDirUnit)
		
		if self.bzrTank.shotsAvailable > 0:
			self.bzrTank.Shoot()
	

class SimpleAgent:
	def __init__(self, hostname, port):

		self.socket = BZRSocket.BZRSocket(hostname, port)

		self.field = Fields()
		self.field.addField("flag", PotentialField.GoalField(370, 0))

		self.tanks = [FieldFollowTank(self.socket.mytanks[0], self.field), FieldFollowTank(self.socket.mytanks[1], self.field)]
	def run(self):
		while True:
			self.socket.mytanks.Update()

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

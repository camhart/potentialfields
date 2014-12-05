
from agent.bzrsocket import BZRSocket, BZRGame
from potentialfields.fields import GoalField
from potentialfields.fieldmanager import FieldManager
import argparse
import time
import cmath
import random
import bzrplot

class SpinningDuckTank:
	def __init__(self, bzrTank, game):
		self.bzrTank = bzrTank
		self.game = game


	def update(self):
		willHit = self.game.willHitEnemy(self.bzrTank)
		if self.bzrTank.shotsAvailable > 0 and willHit:
			self.bzrTank.shoot()

		sideRotation = cmath.rect(1.0, cmath.pi * 0.25) * self.bzrTank.direction
		offsetToOrigin = complex(0, -400)-self.bzrTank.position

		if abs(offsetToOrigin) < 100:
			self.bzrTank.setSpeed(0.0)
			self.bzrTank.rotateTowards(cmath.rect(1, cmath.pi * 0.75))
		else:
			self.bzrTank.setSpeed(1.0)
			if abs(offsetToOrigin) > 0:
				offsetToOrigin /= abs(offsetToOrigin)

			self.bzrTank.setAngularVelocity(sideRotation.real * offsetToOrigin.real + sideRotation.imag * offsetToOrigin.imag)

class SimpleAgent:
	def __init__(self, hostname, port):

		self.socket = BZRSocket(hostname, port)
		self.game = BZRGame(self.socket)

		self.tanks = []
		for tank in self.socket.mytanks.tanks:
			self.tanks.append(SpinningDuckTank(tank, self.game))


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

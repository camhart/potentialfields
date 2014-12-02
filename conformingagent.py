
from agent.bzrsocket import BZRSocket
import argparse
import time
import cmath
import random

TURN_TIME = 15	#time to wait until agent turns

class ConformingTank:
	def __init__(self, bzrTank):
		self.bzrTank = bzrTank
		# self.nextShootTime = time.clock() + random.uniform(1.5, 2.5)
		self.nextTurnTime = time.time()	#15 seconds until turn

		self.bzrTank.setSpeed(0.0)

	def update(self):
		# correctedTime = time.clock() * 100

		# if correctedTime >= self.nextShootTime:
		# 	self.bzrTank.shoot()
		# 	self.nextShootTime = correctedTime + random.uniform(1.5, 2.5)

		if time.time() >= self.nextTurnTime:
			self.bzrTank.rotateTowards(self.bzrTank.direction * cmath.rect(1, cmath.pi / 2.5))
			self.nextTurnTime = time.time() + TURN_TIME
			self.bzrTank.setSpeed(0.0)
		
		# else:
		# 	self.bzrTank.setSpeed(1.0)

		if self.bzrTank.velocity == complex(0, 0):
			self.bzrTank.setSpeed(1.0)
		pass


class ConformingAgent:
	def __init__(self, hostname, port):
		self.socket = BZRSocket(hostname, port)
		self.tanks = []
		for tank in self.socket.mytanks.tanks:
			self.tanks.append(ConformingTank(tank))

	def run(self):
		while True:
			self.socket.mytanks.update()

			for tank in self.tanks:
				tank.update()

			time.sleep(0)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog="bzrsocket")
	parser.add_argument("--host", help="the host to connect to")
	parser.add_argument("--port", type=int, help="the port to connect to")
	args = parser.parse_args()

	if args.host == None or args.port == None:
		parser.print_help()
	else:
		conformingAgent = ConformingAgent(args.host, args.port)
		conformingAgent.run()

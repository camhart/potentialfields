
from agent.bzrsocket import BZRSocket
import argparse
import time
import cmath
import random

class WildTank:
	def __init__(self, bzrTank):
		self.bzrTank = bzrTank
		# self.nextShootTime = time.clock() + random.uniform(1.5, 2.5)
		self.nextTurnTime = time.time() + random.uniform(1, 15)
		self.nextSpeedTime = time.time() + 2 + random.uniform(1, 2)

		# self.bzrTank.setSpeed(1.0)

	def update(self):
		correctedTime = time.time()

		# if correctedTime >= self.nextShootTime:
		# 	self.bzrTank.shoot()
		# 	self.nextShootTime = correctedTime + random.uniform(1.5, 2.5)

		if correctedTime >= self.nextTurnTime:
			# self.bzrTank.rotateTowards(self.bzrTank.direction * cmath.rect(1, cmath.pi / random.randint(1, 5)))
			# print(self.bzrTank.direction * cmath.rect(1, cmath.pi / 4))
			# print(cmath.rect(1, cmath.pi / 4))
			# print(cmath.pi / 4)
			self.bzrTank.rotateTowards(self.bzrTank.direction * cmath.rect(1, cmath.pi / random.random()))
			self.nextTurnTime = correctedTime + random.uniform(1, 12)

		elif correctedTime >= self.nextSpeedTime:
			self.bzrTank.setSpeed(random.random())
			self.nextSpeedTime = correctedTime + random.uniform(1, 2)


class WildAgent:
	def __init__(self, hostname, port):
		self.socket = BZRSocket(hostname, port)
		self.tanks = []
		for tank in self.socket.mytanks.tanks:
			self.tanks.append(WildTank(tank))

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
		wildAgent = WildAgent(args.host, args.port)
		wildAgent.run()

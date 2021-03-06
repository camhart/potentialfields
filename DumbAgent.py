
from Agent import BZRSocket
import argparse
import time
import cmath
import random

class DumbTank:
	def __init__(self, bzrTank):
		self.bzrTank = bzrTank
		self.nextShootTime = time.clock() + random.uniform(1.5, 2.5)
		self.nextTurnTime = time.clock() + random.uniform(6, 8)

		self.bzrTank.SetSpeed(1.0)

	def Update(self):
		correctedTime = time.clock() * 100

		if correctedTime >= self.nextShootTime:
			self.bzrTank.Shoot()
			self.nextShootTime = correctedTime + random.uniform(1.5, 2.5)

		if correctedTime >= self.nextTurnTime:
			self.bzrTank.RotateTowards(self.bzrTank.direction * cmath.rect(1, cmath.pi / 3))
			self.nextTurnTime = correctedTime + random.uniform(6, 8)

		if self.bzrTank.velocity == complex(0, 0):
			self.bzrTank.SetSpeed(1.0)
	

class DumbAgent:
	def __init__(self, hostname, port):
		self.socket = BZRSocket.BZRSocket(hostname, port)
		self.tanks = [DumbTank(self.socket.mytanks[0]), DumbTank(self.socket.mytanks[1])]
	def Run(self):
		while True:
			self.socket.mytanks.Update()

			for tank in self.tanks:
				tank.Update()
			
			time.sleep(0)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog="BZRSocket")
	parser.add_argument("--host", help="the host to connect to")
	parser.add_argument("--port", type=int, help="the port to connect to")
	args = parser.parse_args()

	if args.host == None or args.port == None:
		parser.print_help()
	else:
		dumbAgent = DumbAgent(args.host, args.port)
		dumbAgent.Run()

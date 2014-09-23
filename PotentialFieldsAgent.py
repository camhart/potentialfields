from Agent import BZRSocket
import argparse
import time
import cmath
import random

from PotentialFields.Fields import Fields

class PotentialFieldsTank:

    def __init__(self, bzrtank):
        self.bzrtank = bzrtank
        self.bzrtank.SetSpeed(1.0)


    def Update(self):
        self.bzrTank.RotateTowards(self.bzrTank.direction * cmath.rect(1, cmath.pi / 3))

class PotentialFieldsAgent:
    def __init__(self, hostname, port):
        self.socket = BZRSocket.BZRSocket(hostname, port)
        self.tanks = [PotentialFieldsTank(self.socket.mytanks[0]), PotentialFieldsTank(self.socket.mytanks[1])]


        #get obstacles


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
        dumbAgent = PotentialFieldsAgent(args.host, args.port)
        dumbAgent.Run()



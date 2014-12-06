import numpy
import math

from kalmanplot import plotFilterPredictions

# matrix H
selectionMatrix = numpy.matrix([
	[1, 0, 0, 0, 0, 0],
	[0, 0, 0, 1, 0, 0]
	])
selectionMatrixTranspose = selectionMatrix.getT()

identity6x6 = numpy.matrix([
	[1, 0, 0, 0, 0, 0],
	[0, 1, 0, 0, 0, 0],
	[0, 0, 1, 0, 0, 0],
	[0, 0, 0, 1, 0, 0],
	[0, 0, 0, 0, 1, 0],
	[0, 0, 0, 0, 0, 1]
	])

zeroAccelerationTolerance = 10
zeroTolerence = 0.0001

def TimestepMatrix(timestep, drag):
	return numpy.matrix([
		[1, timestep, timestep * timestep * 0.5, 0, 0, 0],
		[0, 1, timestep, 0, 0, 0],
		[0, -drag, 1, 0, 0, 0],
		[0, 0, 0, 1, timestep, timestep * timestep * 0.5],
		[0, 0, 0, 0, 1, timestep],
		[0, 0, 0, 0, -drag, 1]
	])

class Filter:
	def __init__(self):
		# matrix sigma_z
		self.inputCovarianceMatrix = numpy.matrix([[25, 0], [0, 25]])
		# matrix u_t
		self.trackedPosition = numpy.matrix([[0]] * 6)
		# matrix sigma_t
		self.trackedCovarianceMatrix = numpy.matrix([
			[100, 0, 0, 0, 0, 0],
			[0, 0.1, 0, 0, 0, 0],
			[0, 0, 0.1, 0, 0, 0],
			[0, 0, 0, 100, 0, 0],
			[0, 0, 0, 0, 0.1, 0],
			[0, 0, 0, 0, 0, 0.1]
			])

		positionCoef = 0.01
		velCoef = 0.1
		acellCoef = 1

		allScalar = 0.01
	
		positionCoef *= allScalar
		velCoef *= allScalar
		acellCoef *= allScalar

		# matrix sigma_x
		self.uncertaintyDistribution = numpy.matrix([

			[positionCoef, 0, 0, 0, 0, 0],
			[0, velCoef, 0, 0, 0, 0],
			[0, 0, acellCoef, 0, 0, 0],
			[0, 0, 0, positionCoef, 0, 0],
			[0, 0, 0, 0, velCoef, 0],
			[0, 0, 0, 0, 0, acellCoef]

		])

	def ResetPosition(self, positionX, positionY):
		self.trackedPosition = numpy.matrix([[positionX], [0], [0], [positionY], [0], [0]])

	# sampleX and sampleY are the samples x and y position of the tank
	# timestep is the time, in seconds, between this sample and the last sample
	def AddSample(self, sampleX, sampleY, timestep):
		# matrix F
		timestepMatrix = TimestepMatrix(timestep, 0)
		transposeTimestep = timestepMatrix.getT()

		# 6x2
		modifiedCovariance = timestepMatrix * self.trackedCovarianceMatrix * transposeTimestep + self.uncertaintyDistribution

		k = modifiedCovariance * selectionMatrixTranspose * ((selectionMatrix * modifiedCovariance * selectionMatrixTranspose + self.inputCovarianceMatrix).getI())
		predictedPosition = timestepMatrix * self.trackedPosition

		sampleAsMatrix = numpy.matrix([[sampleX],[sampleY]])
		self.trackedPosition = predictedPosition + k * (sampleAsMatrix - selectionMatrix * predictedPosition)
		self.trackedCovarianceMatrix = (identity6x6 - k * selectionMatrix) * modifiedCovariance

		# plotFilterPredictions(self.trackedPosition.item(0), self.trackedPosition.item(3), sampleX, sampleY)
		# fx, fy = self.Predict(3.5)
		# plotFilterPredictions(fx, fy, sampleX, sampleY)
		# futureX, futureY = self.Predict(3.5)


	def Predict(self, futureTime):
		result = TimestepMatrix(futureTime, 0) * self.trackedPosition
		return result.item(0), result.item(3)
		

	# x, y is the position of the projectile
	# vx, vy is the velocity of the projectile
	def WillProjectileHit(self, x, y, vx, vy, hitRadius, shotLifetime, radiusDistanceScalar = 3):
		positionXDiff = self.trackedPosition.item(0) - x
		posttionYDiff = self.trackedPosition.item(3) - y
		velXDiff = self.trackedPosition.item(1) - vx
		velYDiff = self.trackedPosition.item(4) - vy

		# caculate the time till the closest approach
		time = -(positionXDiff * velXDiff + posttionYDiff * velYDiff) / (velXDiff * velXDiff + velYDiff * velYDiff)

		if time < 0:
			return False

		if time > shotLifetime:
			time = shotLifetime

		futureX, futureY = self.Predict(time)

		futureProjX = x + vx * time
		futureProjY = y + vy * time
			
		futureOffX = futureX - futureProjX
		futureOffY = futureY - futureProjY

		actualRadius = hitRadius * (1 + (radiusDistanceScalar - 1) * time / shotLifetime)
		
		return futureOffX * futureOffX + futureOffY * futureOffY <= actualRadius * actualRadius

if __name__ == "__main__":
	linearTest = Filter()

	for i in range(100):
		linearTest.AddSample(i * 1.5, i * 0.5, 1)

	print(linearTest.Predict(1.0))
	print(linearTest.Predict(2.0))
	print(linearTest.Predict(3.0))
	print(linearTest.WillProjectileHit(150, 49, 0, 1, 0.5)) 

	quadraticTest = Filter()

	for i in range(100):
		quadraticTest.AddSample(i * 1.0, i * i - i * 100.0, 1)

	print(quadraticTest.Predict(1.0))
	print(quadraticTest.Predict(2.0))
	print(quadraticTest.Predict(3.0))
	print(quadraticTest.WillProjectileHit(100, -1, 0, 1, 0.5)) 
	

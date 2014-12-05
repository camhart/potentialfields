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

zeroAccelerationTolerance = 1000
zeroTolerence = 0.0001

def TimeTillHit(projPos, projVel, targetPos, targetVel, targetAccel):
	if abs(targetAccel) < zeroAccelerationTolerance:
		velDiff = targetVel - projVel
		if abs(velDiff) < zeroTolerence:
			return -1
		else:
			return (projPos - targetPos) / velDiff
	else:
		a = 0.5 * targetAccel
		b = targetVel - projVel
		c = targetPos - projPos
		insideSqrt = b * b - 4 * a * c

		if insideSqrt < 0.0:
			return -1

		valSqrt = math.sqrt(insideSqrt)

		closerValue = (b - valSqrt) / targetAccel
		furtherValue = (b + valSqrt) / targetAccel
		
		if closerValue > furtherValue:
			# swap the two
			closerValue, furtherValue = furtherValue, closerValue
			

		if closerValue > 0:
			return closerValue
		else:
			return furtherValue

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

		futureX, futureY = self.Predict(3.5)

	def Predict(self, futureTime):
		result = TimestepMatrix(futureTime, 0) * self.trackedPosition
		return result.item(0), result.item(3)
		

	# x, y is the position of the projectile
	# vx, vy is the velocity of the projectile
	def WillProjectileHit(self, x, y, vx, vy, hitRadius, shotLifetime):
		time = TimeTillHit(x, vx, self.trackedPosition.item(0), self.trackedPosition.item(1), self.trackedPosition.item(2))

		if time < 0:
			time = TimeTillHit(y, vy, self.trackedPosition.item(3), self.trackedPosition.item(4), self.trackedPosition.item(5))

		if time < 0:
			return False

		if time > shotLifetime:
			return False

		futureX, futureY = self.Predict(time)

		futureProjX = x + vx * time
		futureProjY = y + vy * time
			
		futureOffX = futureX - futureProjX
		futureOffY = futureY - futureProjY

		#plotFilterPredictions(futureX, futureY, futureProjX, futureProjY)

		return futureOffX * futureOffX + futureOffY * futureOffY <= hitRadius * hitRadius

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
	

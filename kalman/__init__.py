import numpy

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

		# matrix sigma_x
		self.uncertaintyDistribution = numpy.matrix([
			[0.1, 0, 0, 0, 0, 0],
			[0, 0.1, 0, 0, 0, 0],
			[0, 0, 100, 0, 0, 0],
			[0, 0, 0, 0.1, 0, 0],
			[0, 0, 0, 0, 0.1, 0],
			[0, 0, 0, 0, 0, 100]
		])

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

	def Predict(self, futureTime):
		result = TimestepMatrix(futureTime, 0) * self.trackedPosition
		return result.item(0), result.item(3)
		

if __name__ == "__main__":
	linearTest = Filter()

	for i in range(100):
		linearTest.AddSample(i * 1.5, i * 0.5, 1)

	print(linearTest.Predict(1.0))
	print(linearTest.Predict(2.0))
	print(linearTest.Predict(3.0))

	quadraticTest = Filter()

	for i in range(100):
		quadraticTest.AddSample(i * 1.0, i * i - i * 100.0, 1)

	print(quadraticTest.Predict(1.0))
	print(quadraticTest.Predict(2.0))
	print(quadraticTest.Predict(3.0))
	

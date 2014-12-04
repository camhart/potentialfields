import matplotlib.pyplot as plt
import random

def plotPositions(x, y, color, widthMin=None, widthMax=None, heightMin=None, heightMax=None):


	if widthMax == None:
		widthMax = max(x)
	if widthMin == None:
		widthMin = min(x)
	if heightMax == None:
		heightMax = max(y)
	if heightMin == None:
		heightMin = min(y)

	plt.xlim(xmax = widthMax)
	plt.xlim(xmin = widthMin)
	plt.ylim(ymax = heightMax)
	plt.ylim(ymin = heightMin)

	plt.scatter(x, y, c=color)

def plotFilterPredictions(px, py, sx, sy):
	plotPositions([px], [py], 'p')
	plotPositions([sx], [sy], 'g', -400, 400, -400, 400)
	# plt.show()

if __name__ == '__main__':

	currentPositions = []
	predictedPositions = []

	width = 100
	height = 100

	for i in range(10):
		currentPositions.append((random.randint(0, width), random.randint(0, height)))

	for i in range(10):
		currentPositions.append((random.randint(0, width), random.randint(0, height)))

	cpx = [x for x,y in currentPositions]
	cpy = [y for x,y in currentPositions]

	ppx = [x for x,y in predictedPositions]
	ppy = [y for x,y in predictedPositions]	


	plotPositions(cpx, cpy, 'r', 0, 100, 0, 100)

	for i in range(10):
		currentPositions[i]= (random.randint(0, width), random.randint(0, height))

	for i in range(10):
		currentPositions[i] = (random.randint(0, width), random.randint(0, height))

	cpx = [x for x,y in currentPositions]
	cpy = [y for x,y in currentPositions]

	ppx = [x for x,y in predictedPositions]
	ppy = [y for x,y in predictedPositions]	

	plotPositions(cpx, cpy, 'b', 0, 100, 0, 100)
	plt.show()

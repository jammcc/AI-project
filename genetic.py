import tetrominoAI
from tetromino import main,runGame
from random import uniform, randint, random
import threading
import Queue
import time

class aiThread(threading.Thread):
	"""docstring for aiThread"""
	def __init__(self, threadID, aiQ):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.aiQ = aiQ
	def run(self):
		while True:
			aiLock.acquire()
			if not self.aiQ.empty():
				ai = self.aiQ.get()
				aiLock.release()
				evaluateFitness(ai)
			else:
				aiLock.release()
				break

def beginMultiTheadEval(seedAI):
	aiQueue = Queue.Queue(len(seedAI))
	for ai in seedAI:
		aiQueue.put(ai)

	threads = []
	for i in range(numThreads):
		thread = aiThread(i, aiQueue)
		thread.start()
		threads.append(thread)
	while not aiQueue.empty():
		pass

	for t in threads:
		t.join()

def beginEvolution(seedAI,num_generations = None,multi=False):
	if num_generations == None:
		num_generations = 1

	for i in range(num_generations):
		print("Generation {0}".format(i))
		if multi:
			beginMultiTheadEval(seedAI)
		else:
			for ai in seedAI:
				evaluateFitness(ai)
		ordered = orderAIs(seedAI)
		seedAI = newGeneration(ordered)

	best = ordered[0]
	print("Score: {0}, Lines: {2}, Weights: {1}".format(best.score,best.weights,best.linesCleared))

#return ordered from best to worst
def orderAIs(ais):
	ordered = []
	while len(ais) != 0:
		bestindex = 0
		bestscore = ais[0].score
		for i in range(1,len(ais)):
			if ais[i].score > bestscore:
				bestscore = ais[i].score
				bestindex = i
		ordered.append(ais.pop(bestindex))
	return ordered

def newGeneration(parentAIs):
	parentAIs.pop(-1)
	parent1 = chooseParents(parentAIs)
	parent2 = parentAIs[1]
	while parent2 == parent1:
		parent2 = chooseParents(parentAIs)
	baby = makeBaby(parent1,parent2)
	parentAIs.append(baby)
	return parentAIs

#choose parents proportional to fitness
def chooseParents(parentAIs):
	totalscore = sum(ai.score for ai in parentAIs)
	i = random()*totalscore
	curr = 0
	for ai in parentAIs:
		curr += ai.score
		if  i < curr:
			return ai
	return parentAIs[randint(0,len(parentAIs)-1)]

def makeBaby(parent1,parent2):
	numweights = len(parent1.weights)
	newWeights = []
	for i in range(numweights):
		weight = 0.0
		if randint(0,1) == 0:
			weight = parent1.weights[i]
		else:
			weight = parent2.weights[i]
		weight = mutation(weight, 0.1)
		newWeights.append(weight)
	return tetrominoAI.TetrominoChromosome(newWeights)

def mutation(orig_weight,mutation_rate):
	if random() < mutation_rate:
		return uniform(-1,1)
	else:
		return orig_weight

def evaluateFitness(ai):
	score, linesCleared = runGame(ai)
	ai.score = score
	ai.linesCleared = linesCleared

def createRandomSeeds(num_seeds):
	seedAI = []
	for i in range(num_seeds):
		distWeight = uniform(-1,1)
		clearWeight = uniform(-1,1)
		holeWeight = uniform(-1,1)
		blockadeWeight = uniform(-1,1)
		heightWeight = uniform(-1,1)
		aggHeightWeight = uniform(-1,1)
		bumpinessWeight = uniform(-1,1)
		weights = [distWeight,clearWeight,holeWeight,blockadeWeight,heightWeight,aggHeightWeight, bumpinessWeight]
		seedAI.append(tetrominoAI.TetrominoChromosome(weights=weights))
	return seedAI

numThreads = 4
aiLock = threading.Lock()
seedAI = createRandomSeeds(16)
beginEvolution(seedAI,10,True)

# main(tetrominoAI.TetrominoChromosome())
import tetrominoAI
from tetromino import main,runGame
from random import uniform, randint, random
from copy import deepcopy
import threading
import Queue
import time

fileName = 'weights.txt'

class aiThread(threading.Thread):
	"""docstring for aiThread"""
	def __init__(self, threadID, aiQ):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.aiQ = aiQ
	def run(self):
		while True:
			global numEvaled
			aiLock.acquire()
			if not self.aiQ.empty():
				ai = self.aiQ.get()
				aiLock.release()
				evaluateFitness(ai)
				with aiLock:
					numEvaled +=1
					newGenStart.notify()
			else:
				aiLock.release()
				break

def beginMultiTheadEval(seedAI, numThreads):
	global numEvaled
	aiQueue = Queue.Queue(len(seedAI))

	with aiLock:
		for ai in seedAI:
			aiQueue.put(ai)

	threads = []
	for i in range(numThreads):
		thread = aiThread(i, aiQueue)
		thread.start()
		threads.append(thread)

	with aiLock:
		while numEvaled != len(seedAI):
			newGenStart.wait()
		numEvaled = 0

	for t in threads:
		t.join()

def beginEvolution(seedAI,num_generations = None,numThreads=0):
	if num_generations == None:
		num_generations = 1

	if numThreads != 0:
		print ('NumThreads: {0}'.format(numThreads))

	for i in range(num_generations):
		print("Generation {0}".format(i))
		if numThreads != 0:
			beginMultiTheadEval(seedAI,numThreads)
		else:
			for ai in seedAI:
				evaluateFitness(ai)
		ordered = orderAIs(seedAI)
		seedAI = newGeneration(ordered)
		with open(fileName, 'a') as f:
			f.write(str(ordered[0].weights) + "|" + str(ordered[0].score) + "|" + str(ordered[0].linesCleared) + "\n")
		print("Score: {0}, Lines: {2}, Weights: {1}".format(ordered[0].score,ordered[0].weights,ordered[0].linesCleared))	

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

#generate entirely new generation of chromosomes
def newGeneration(parentAIs):
	babies = []
	for i in range(len(parentAIs)):
		parent1 = chooseParents(parentAIs)
		tempparents = deepcopy(parentAIs)
		parent2 = chooseParents(tempparents)
		baby = makeBaby(parent1,parent2)
		babies.append(baby)
	return babies

#choose parents proportional to fitness
def chooseParents(parentAIs):
	totalscore = sum(ai.score for ai in parentAIs)
	i = random()*totalscore
	curr = 0
	for ai in parentAIs:
		curr += ai.score
		if  i < curr:
			return ai
	rand = randint(0,len(parentAIs)-1)
	return parentAIs[rand]

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
		scoreWeight = uniform(-1,1)
		weights = [distWeight,clearWeight,holeWeight,blockadeWeight,heightWeight,aggHeightWeight, bumpinessWeight, scoreWeight]
		seedAI.append(tetrominoAI.TetrominoChromosome(weights=weights,useNext=False))
	seedAI = []
	for i in range(num_seeds):
		seedAI.append(tetrominoAI.TetrominoChromosome(weights = [0.29273680972498917, -0.35995754766161214, 0.012633707025612395, -0.2431462816304657, 0.08325424652896585, -0.7865135453937053, -0.1742107912531552, 0.3584059853811308]))
	return seedAI

numThreads = 0
aiLock = threading.Lock()
numEvaled = 0
newGenStart = threading.Condition(aiLock)
seedAI = createRandomSeeds(4)
beginEvolution(seedAI,4,numThreads=numThreads)


# main(tetrominoAI.TetrominoChromosome(weights=[0.29273680972498917, -0.7551627206341611, -0.10698876478751984, -0.2431462816304657, 0.08325424652896585, -0.7865135453937053, -0.1742107912531552, 0.3584059853811308]))
# main(tetrominoAI.TetrominoChromosome(weights=[0.04406910518575535, -0.8239039168154034, -0.10698876478751984, -0.2431462816304657, 0.08325424652896585, -0.7865135453937053, -0.29575025661696075, 0.3584059853811308]))
# main(tetrominoAI.TetrominoChromosome(useNext=True,weights=[0.04406910518575535, -0.7551627206341611, -0.10698876478751984, -0.2431462816304657, 0.08325424652896585, -0.7865135453937053, -0.1742107912531552, 0.3584059853811308]))
# main()

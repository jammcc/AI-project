import tetrominoAI
import parser
from tetromino import main,runGame
from random import uniform, randint, random
from copy import deepcopy
import threading
import Queue
import time

aiLock = threading.Lock()
numEvaled = 0
newGenStart = threading.Condition(aiLock)

class aiThread(threading.Thread):
	"""docstring for aiThread"""
	def __init__(self, threadID, aiQ,lineLimit=100):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.aiQ = aiQ
		self.lineLimit = lineLimit
	def run(self):
		while True:
			global numEvaled
			aiLock.acquire()
			if not self.aiQ.empty():
				ai = self.aiQ.get()
				aiLock.release()
				evaluateFitness(ai,self.lineLimit)
				with aiLock:
					numEvaled +=1
					newGenStart.notify()
			else:
				aiLock.release()
				break

def beginMultiTheadEval(self, seedAI, numThreads):
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

def beginEvolution(seedAI,num_generations = None,numThreads=0,lineLimit=100):
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
				evaluateFitness(ai,lineLimit=lineLimit)
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
def newGeneration(parentAIs, elitism=True):
	babies = []
	if elitism: #remove weakest half, keep top quarter, make babies from top half
		tophalf = parentAIs[:len(parentAIs)/2]
		babies = parentAIs[:len(parentAIs)/4]
		for i in range(len(parentAIs) - len(parentAIs)/4):
			parent1 = chooseParents(tophalf)
			tempparents = list(tophalf)
			tempparents.remove(parent1)
			parent2 = chooseParents(tempparents)
			baby = makeBaby(parent1,parent2)
			babies.append(baby)
	else:
		for i in range(len(parentAIs)):
			parent1 = chooseParents(parentAIs)
			tempparents = list(parentAIs)
			tempparents.remove(parent1)
			parent2 = chooseParents(tempparents)
			baby = makeBaby(parent1,parent2)
			babies.append(baby)
	return babies

#choose parents proportional to fitness
def chooseParents(parentAIs):
	totalscore = sum(ai.score for ai in parentAIs) + len(parentAIs)
	i = random()*totalscore
	curr = 0
	for ai in parentAIs:
		curr += ai.score + 1
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

def evaluateFitness(ai,lineLimit=100):
	score, linesCleared = runGame(ai,lineLimit=lineLimit)
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
		wellWeight = uniform(-1,1)
		altDiffWeight = uniform(-1,1)
		hoRoughWeight = uniform(-1,1)
		vertRoughWeight = uniform(-1,1)
		weightedHolesWeight = uniform(-1,1)
		weights = [distWeight,clearWeight,holeWeight,blockadeWeight,heightWeight,aggHeightWeight, bumpinessWeight, scoreWeight,wellWeight,altDiffWeight,hoRoughWeight,vertRoughWeight,weightedHolesWeight]
		seedAI.append(tetrominoAI.TetrominoChromosome(weights=weights,useNext=False))
	seedAI = []
	for i in range(num_seeds):
		seedAI.append(tetrominoAI.TetrominoChromosome(weights = [-0.04437397471669002, 0.7479801381485471, 0.8362922496457046, -0.24011961504107826, -0.375625790426511, 0.8987155097012198, -0.8398365465268014, 0.39980827155830134, -0.43912135712982825, 0.8628568355776391, -0.40295238222356633, -0.8097107039859499, -0.8920129226509008]))
	return seedAI


fileName = 'weights100000lines16NR8colSeeds200gen.txt'
numThreads = 0
seedAI = createRandomSeeds(16)
beginEvolution(seedAI,200,numThreads=numThreads,lineLimit=100000)


# main(tetrominoAI.TetrominoChromosome(weights=[0.29273680972498917, -0.7551627206341611, -0.10698876478751984, -0.2431462816304657, 0.08325424652896585, -0.7865135453937053, -0.1742107912531552, 0.3584059853811308]))
# main(tetrominoAI.TetrominoChromosome(weights=[0.04406910518575535, -0.8239039168154034, -0.10698876478751984, -0.2431462816304657, 0.08325424652896585, -0.7865135453937053, -0.29575025661696075, 0.3584059853811308]))
# main(tetrominoAI.TetrominoChromosome(useNext=True,weights=[0.04406910518575535, -0.7551627206341611, -0.10698876478751984, -0.2431462816304657, 0.08325424652896585, -0.7865135453937053, -0.1742107912531552, 0.3584059853811308]))

# main(tetrominoAI.TetrominoChromosome(weights=[0.14153234653955638, 0.16899177050877512, -0.9987792538542004, -0.8453062347116065, 0.23130316007976615, 0.18111870466738278, -0.2900956878696639, 0.28976659359991985]))
# main(tetrominoAI.TetrominoChromosome(weights=[0.35272186636082536, 0.27988300741810423, -0.994208214509138, -0.7531771675316605, 0.495530410285022, -0.8559373911265069, -0.2900956878696639, 0.17112501629360133]))
# main(tetrominoAI.TetrominoChromosome(weights=[0.5805661700520182, 0.7607647443126826, -0.437695807431314, -0.052252583297341504, 0.964624551596726, 0.3371063413480089, -0.5409979276979748, 0.8420016513789197, -0.0018730300248084308, 0.0019510645601550358, -0.6158826968068729, -0.41595520028074606, -0.773841921631903]),lineLimit=100000)
# main(tetrominoAI.TetrominoChromosome(useNext=True,weights=[0.4366306442721901, -0.42278664125412124, -0.20514499908822148, -0.052252583297341504, 0.2810089965206035, 0.3371063413480089, -0.4890056043233375, 0.8339003972378074, -0.0018730300248084308, 0.6494234224765245, -0.6158826968068729, -0.41595520028074606, -0.773841921631903]),lineLimit=100000)
											             # [distWeight,         clearWeight,           holeWeight,           blockadeWeight,        heightWeight,       aggHeightWeight,     bumpinessWeight,     scoreWeight,        wellWeight,             altDiffWeight,      hoRoughWeight,        vertRoughWeight,     weightedHolesWeight]
											             	# [0.4366306442721901, 0.21403505208600615, -0.20514499908822148, -0.052252583297341504, 0.2810089965206035, 0.70890637968575, -0.4890056043233375, 0.48216995425076203, -0.0018730300248084308, 0.6494234224765245, -0.6158826968068729, 0.6892131250660432, -0.773841921631903]

weight =  [0, -0.1, -0.959944778488526, -0.7565604302338298, 0.3189338415448301, -0.917976747836295, -0.2781958880440105, 0.62304571252862946, 0.15834714777029513, 0.08137614982575325, -0.3685169906372381, -0.20672949820738218]


# main(tetrominoAI.TetrominoChromosome(weights=[-0.04437397471669002, 0.7479801381485471, 0.8362922496457046, -0.24011961504107826, -0.375625790426511, 0.8987155097012198, -0.8398365465268014, 0.39980827155830134, -0.43912135712982825, 0.8628568355776391, -0.40295238222356633, -0.8097107039859499, -0.8920129226509008]),lineLimit=100000)

# main(tetrominoAI.TetrominoChromosome(weights=weight))

# hundlines_16nr_200gen = 'weights100lines16NRseeds200gen.txt'
# parsedAIs1 = parser.Parser(hundlines_16nr_200gen)
# parsedAIs1.plotScoreLineRatio()
# parsedAIs1.plotScores()

# hundlines_16r_200gen = 'weights100lines16Rseeds200gen.txt'
# parsedAIs2 = parser.Parser(hundlines_16r_200gen)
# parsedAIs2.plotScores()
# parsedAIs2.plotLinesCleared()
# parsedAIs2.plotScoreLineRatio()

# parsedAIs3 = parser.Parser('weights.txt')
# parsedAIs3.plotLinesCleared()

# main()

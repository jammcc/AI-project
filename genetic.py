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
		tetrisWeight = uniform(-1,1)
		weights = [distWeight,clearWeight,holeWeight,blockadeWeight,heightWeight,aggHeightWeight, bumpinessWeight, scoreWeight,wellWeight,altDiffWeight,hoRoughWeight,vertRoughWeight,weightedHolesWeight,tetrisWeight]
		seedAI.append(tetrominoAI.TetrominoChromosome(weights=weights,useNext=False))
	# seedAI = []
	# for i in range(num_seeds):
	# 	seedAI.append(tetrominoAI.TetrominoChromosome(weights = [-0.04437397471669002, 0.7479801381485471, 0.8362922496457046, -0.24011961504107826, -0.375625790426511, 0.8987155097012198, -0.8398365465268014, 0.39980827155830134, -0.43912135712982825, 0.8628568355776391, -0.40295238222356633, -0.8097107039859499, -0.8920129226509008]))
	return seedAI

#FOLLOWING LINES RUN THE PROGRAM

#uncomment the following 4 lines to run the genetic algorithm training ================
# fileName = 'weights.txt'
# numThreads = 0
# seedAI = createRandomSeeds(16)
# beginEvolution(seedAI,100,numThreads=numThreads,lineLimit=100)

#uncomment this line to run the AI that can last practically indefinitely==============
main(tetrominoAI.TetrominoChromosome(useNext=True,weights=[0.4366306442721901, -0.42278664125412124, -0.20514499908822148, -0.052252583297341504, 0.2810089965206035, 0.3371063413480089, -0.4890056043233375, 0.8339003972378074, -0.0018730300248084308, 0.6494234224765245, -0.6158826968068729, -0.41595520028074606, -0.773841921631903]),lineLimit=100000)

#uncomment this line to run the AI that tends to "tetris" (clear lines concurrently)=========
# main(tetrominoAI.TetrominoChromosome(weights=[0.8977030239691923, 0.0006318680531292031, 0.07372662458714441, 0.5007097883265044, 0.46319363761516175, -0.569519613459228, -0.8521767580007076, -0.12289110995927133, 0.3316333640697906, 0.5678085138088147, -0.02797113020725539, 0.4461532705201614, -0.974629849419808, 0.5629610071455657]),lineLimit=100)


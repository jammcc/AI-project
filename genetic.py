import tetrominoAI
from tetromino import main,runGame
from random import uniform

def beginEvolution(seedAI):

	best = None
	score = None
	for ai in seedAI:
		evaluateFitness(ai)
		if best == None or ai.score > score:
			best = ai
			score = ai.score

	print("Score: {0}, Weights: {1}".format(best.score,best.weights))


def evaluateFitness(ai):
	ai.score = runGame(ai)

def createRandomSeeds(num_seeds):
	seedAI = [tetrominoAI.TetrominoChromosome()]
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

seedAI = createRandomSeeds(0)
beginEvolution(seedAI)

# main(tetrominoAI.TetrominoChromosome())
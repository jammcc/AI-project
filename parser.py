import matplotlib.pyplot as plt
from tetrominoAI import TetrominoChromosome

class Parser:
	def __init__(self,filename):
		self.ais = self.parseWeightFile(filename)

	def parseWeightFile(self,filename):
		ais = []
		with open(filename, 'r') as f:
			for line in f:
				s = line.split('|')
				s_weights = s[0].lstrip('[').rstrip(']').split(',')
				weights = [float(w) for w in s_weights]
				score = int(s[1])
				linesCleared = int(s[2])
				ai = TetrominoChromosome(weights = weights)
				ai.score = score
				ai.linesCleared = linesCleared
				ais.append(ai)
		return ais

	def plotScores(self):
		plt.plot([i for i in range(len(self.ais))], [ai.score for ai in self.ais])
		# plt.axis([0, len(ai, 0, 20])
		plt.show()

	def plotLinesCleared(self):
		plt.plot([i for i in range(len(self.ais))], [ai.linesCleared for ai in self.ais])
		# plt.axis([0, len(ai, 0, 20])
		plt.show()
from tetrominoAI import TetrominoChromosome

class Parser:
	def __init__(self):
		return

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
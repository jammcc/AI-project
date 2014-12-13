import random, time, pygame, sys
from pygame.locals import *
from constants import *
from tetromino import isValidPosition, addToBoard, removeCompleteLines, calculateScore
from random import randint
from copy import deepcopy

#piece has shape, rotation, x, y, color

distWeight = 0.0
clearWeight = 0.99275
holeWeight = -0.46544
blockadeWeight = -0.25
heightWeight = 0
aggHeightWeight = -0.66590
bumpinessWeight = -0.24077
scoreWeight = 1.0

testWeights = [distWeight,clearWeight,holeWeight,blockadeWeight,heightWeight,aggHeightWeight, bumpinessWeight,scoreWeight]

class TetrominoChromosome:
	def __init__(self, weights=testWeights, useNext = False):
		self.weights = weights
		self.score = 0
		self.linesCleared = 0
		self.useNext = useNext

	def randomMove(self,board,piece):
		tempPiece = dict(piece)
		numRotations = len(PIECES[piece['shape']])
		tempPiece['x'] = randint(-2,BOARDWIDTH-1)
		tempPiece['rotation'] = randint(0,numRotations-1)
		tempPiece['y'] += self.distToBottom(board,tempPiece)
			
		return tempPiece if isValidPosition(board,tempPiece) else piece

	def bestMove(self,board, piece, nextPiece = None):
		if not self.useNext:
			nextPiece = None
		#perform BFS
		tpiece = dict(piece)
		pieceId = piece['shape']
		numRotations = len(PIECES[pieceId])
		best_piece = dict(piece)
		best_score = self.getScore(board,tpiece,nextPiece=nextPiece)
		best_piece['y'] += self.distToBottom(board,best_piece)
		for position in range(-2,BOARDWIDTH):
			for rot in range(numRotations):
				tempPiece = dict(piece)
				tempPiece['x'] = position
				tempPiece['rotation'] = rot
				tempPiece['y'] = 0
				if isValidPosition(board, tempPiece):
					score = self.getScore(board,tempPiece, nextPiece=nextPiece)
					# tempPiece['y'] = piece['y']
					if best_score == None:
						best_piece = tempPiece
						best_score = score
					elif score > best_score:
						best_score = score
						best_piece = tempPiece
		temp_piece = dict(best_piece)
		b,ls = self.getAllScores(board,temp_piece)
		# print("Distance: {0}, Clear: {1}, Holes: {2}, Blockades: {3}, Height: {4}, Agg height: {5}, bumpiness:{6}".format(ls[0],ls[1],ls[2],ls[3], ls[4], ls[5],ls[6]))
		return best_piece, best_score

	def getScore(self,board, piece,nextPiece=None):

		newBoard,scores = self.getAllScores(board,piece)
		
		next_best_score = 0
		if nextPiece != None:
			placeholder, next_best_score = self.bestMove(newBoard,nextPiece)
		
		score = 0
		for w,s in zip(self.weights,scores):
			score += w*s

		return score + next_best_score

	def getAllScores(self,board,piece):
		tempPiece = piece #dict(piece)
		newBoard = deepcopy(board)
		distScore = self.distToBottom(newBoard,tempPiece)

		tempPiece['y'] += distScore
		# if tempPiece['y'] < 0:
		# 	print ("=========distScore: {0}, y: {1}, x: {2} ===============".format(distScore,tempPiece['y'],tempPiece['x']))
		if tempPiece['y'] > -2 and isValidPosition(newBoard,tempPiece):
			addToBoard(newBoard,tempPiece)

		clearScore = removeCompleteLines(newBoard)
		level = int(clearScore / 10) + 1
		scoreScore = calculateScore(clearScore,level)
		holeScore,blockadeScore, height, aggregate_height, bumpiness = self.scoresOfBoard(newBoard)
		# print("Distance: {0}, Clear: {1}, Holes: {2}, Blockades: {3}, Height: {4}, bumpiness:{5}".format(distScore,clearScore,holeScore,blockadeScore, height,bumpiness))
		return newBoard, [distScore, clearScore, holeScore, blockadeScore, height, aggregate_height, bumpiness,scoreScore]

	def distToBottom(self,board,piece):
		for i in range(1,BOARDHEIGHT+2):
			if not isValidPosition(board, piece, adjY=i):
				break
		return i-1

	def scoresOfBoard(self,board):
		holes = 0.0
		blockades = 0.0
		height = 0.0
		aggregate_height = 0.0
		prev_col_height = None
		bumpiness = 0.0
		for column in board:
			h, b, colheight= self.scoresPerColumn(column)
			holes += h
			blockades += b
			if colheight > height:
				height = colheight
			aggregate_height +=  colheight
			if prev_col_height != None:
				bumpiness += abs(colheight - prev_col_height)
			prev_col_height = colheight
		return holes, blockades, height, aggregate_height, bumpiness

	def scoresPerColumn(self,column):
		holes = 0.0
		blockades = 0.0
		curr_blockades = 0.0
		blocksInColumn = 0.0
		blockExists = False
		columnHeight = BOARDHEIGHT

		for block in column:
			if block != BLANK:
				blocksInColumn += 1
				curr_blockades += 1
				blockExists = True
			if block == BLANK:
				blockades += curr_blockades
				curr_blockades = 0
				if blocksInColumn != 0:
					holes += 1
				if blocksInColumn == 0:
					columnHeight -= 1.0
		return holes, blockades, columnHeight



#!/usr/bin/env python3

#Author: Zhiwei Luo

from task import Strategy, NetworkInterface
from time import sleep
import math
from operator import itemgetter
import sys

class StrategyTestProgress(Strategy):
	progress = 10

	def checkFinished(self):
		return self.progress <= 0

	def go(self):
		self.progress = self.progress - 1
		print(self.progress)

class StrategyTestCount(Strategy):
	progress = 0

	def checkFinished(self):
		return self.progress > 10

	def go(self):
		self.progress = self.progress + 1
		print(self.progress)
		sleep(1)

class StrategyTestGoDown(Strategy):
	mouse = None
	mapPainter = None
	progress = 0

	def __init__(self, mouse, mapPainter):
		self.mouse = mouse
		self.mapPainter = mapPainter

	def checkFinished(self):
		return self.progress >= 1

	def go(self):
		self.progress = self.progress + 1
		print(self.progress)
		sleep(1)
		self.mouse.goDown()
		self.mouse.goDown()
		self.mouse.goDown()
		self.mouse.goDown()
		self.mouse.goRight()
		self.mouse.goUp()
		cell = self.mouse.mazeMap.getCell(self.mouse.x, self.mouse.y)
		self.mapPainter.putRobotInCell(cell)
		sleep(1)

class StrategyTestDFS(Strategy):
	mouse = None
	mapPainter = None
	isVisited = []
	path = []
	isBack = False

	def __init__(self, mouse, mapPainter):
		self.mouse = mouse
		self.mapPainter = mapPainter
		self.isVisited = [[0 for i in range(self.mouse.mazeMap.width)] for j in range(self.mouse.mazeMap.height)]
		self.isVisited[self.mouse.x][self.mouse.y] = 1

	def checkFinished(self):
		return self.isBack

	def go(self):
		cell = self.mouse.mazeMap.getCell(self.mouse.x, self.mouse.y)
		self.mapPainter.drawCell(cell, 'grey')

		if self.mouse.canGoLeft() and not self.isVisited[self.mouse.x-1][self.mouse.y]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x-1][self.mouse.y] = 1
			self.mouse.goLeft()
		elif self.mouse.canGoUp() and not self.isVisited[self.mouse.x][self.mouse.y-1]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x][self.mouse.y-1] = 1
			self.mouse.goUp()
		elif self.mouse.canGoRight() and not self.isVisited[self.mouse.x+1][self.mouse.y]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x+1][self.mouse.y] = 1
			self.mouse.goRight()
		elif self.mouse.canGoDown() and not self.isVisited[self.mouse.x][self.mouse.y+1]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x][self.mouse.y+1] = 1
			self.mouse.goDown()
		else:
			if len(self.path) != 0:
				x, y = self.path.pop()
				if x < self.mouse.x:
					self.mouse.goLeft()
				elif x > self.mouse.x:
					self.mouse.goRight()
				elif y < self.mouse.y:
					self.mouse.goUp()
				elif y > self.mouse.y:
					self.mouse.goDown()
			else:
				self.isBack = True

		cell = self.mouse.mazeMap.getCell(self.mouse.x, self.mouse.y)
		self.mapPainter.putRobotInCell(cell)
		sleep(0.05)

class StrategyTestMultiDFS(Strategy):
	mouse = None
	isVisited = []
	path = []
	isBack = False
	network = None

	def __init__(self, mouse):
		self.mouse = mouse
		self.isVisited = [[0 for i in range(self.mouse.mazeMap.width)] for j in range(self.mouse.mazeMap.height)]
		self.isVisited[self.mouse.x][self.mouse.y] = 1
		self.network = NetworkInterface()
		self.network.initSocket()
		self.network.startReceiveThread()

	def checkFinished(self):
		return self.isBack

	def go(self):
		self.mouse.senseWalls()
		print(self.mouse.getCurrentCell().getWhichIsWall())
		sendData = {'x': self.mouse.x, 'y':self.mouse.y, 'up': not self.mouse.canGoUp(), 'down': not self.mouse.canGoDown(), 'left': not self.mouse.canGoLeft(), 'right': not self.mouse.canGoRight()}
		self.network.sendStringData(sendData)
		recvData = self.network.retrieveData()
		while recvData:
			otherMap = recvData
			cell = self.mouse.mazeMap.getCell(otherMap['x'], otherMap['y'])
			self.isVisited[otherMap['x']][otherMap['y']] = 1
			if otherMap['up']: self.mouse.mazeMap.setCellUpAsWall(cell)
			if otherMap['down']: self.mouse.mazeMap.setCellDownAsWall(cell)
			if otherMap['left']: self.mouse.mazeMap.setCellLeftAsWall(cell)
			if otherMap['right']: self.mouse.mazeMap.setCellRightAsWall(cell)
			recvData = self.network.retrieveData()

		if self.mouse.canGoLeft() and not self.isVisited[self.mouse.x-1][self.mouse.y]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x-1][self.mouse.y] = 1
			self.mouse.goLeft()
		elif self.mouse.canGoUp() and not self.isVisited[self.mouse.x][self.mouse.y-1]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x][self.mouse.y-1] = 1
			self.mouse.goUp()
		elif self.mouse.canGoRight() and not self.isVisited[self.mouse.x+1][self.mouse.y]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x+1][self.mouse.y] = 1
			self.mouse.goRight()
		elif self.mouse.canGoDown() and not self.isVisited[self.mouse.x][self.mouse.y+1]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x][self.mouse.y+1] = 1
			self.mouse.goDown()
		else:
			if len(self.path) != 0:
				x, y = self.path.pop()
				if x < self.mouse.x:
					self.mouse.goLeft()
				elif x > self.mouse.x:
					self.mouse.goRight()
				elif y < self.mouse.y:
					self.mouse.goUp()
				elif y > self.mouse.y:
					self.mouse.goDown()
			else:
				self.isBack = True

		sleep(0.5)

class StrategyTestDFSEV3(Strategy):
	mouse = None
	#mapPainter = None
	isVisited = []
	path = []
	isBack = False

	def __init__(self, mouse):
		self.mouse = mouse
		#self.mapPainter = mapPainter
		self.isVisited = [[0 for i in range(self.mouse.mazeMap.width)] for j in range(self.mouse.mazeMap.height)]
		self.isVisited[self.mouse.x][self.mouse.y] = 1

	def checkFinished(self):
		return self.isBack

	def go(self):
		#cell = self.mouse.mazeMap.getCell(self.mouse.x, self.mouse.y)
		#self.mapPainter.drawCell(cell, 'grey')
		self.mouse.senseWalls()
		print(self.mouse.getCurrentCell().getWhichIsWall())

		if self.mouse.canGoLeft() and not self.isVisited[self.mouse.x-1][self.mouse.y]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x-1][self.mouse.y] = 1
			self.mouse.goLeft()
		elif self.mouse.canGoUp() and not self.isVisited[self.mouse.x][self.mouse.y-1]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x][self.mouse.y-1] = 1
			self.mouse.goUp()
		elif self.mouse.canGoRight() and not self.isVisited[self.mouse.x+1][self.mouse.y]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x+1][self.mouse.y] = 1
			self.mouse.goRight()
		elif self.mouse.canGoDown() and not self.isVisited[self.mouse.x][self.mouse.y+1]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x][self.mouse.y+1] = 1
			self.mouse.goDown()
		else:
			if len(self.path) != 0:
				x, y = self.path.pop()
				if x < self.mouse.x:
					self.mouse.goLeft()
				elif x > self.mouse.x:
					self.mouse.goRight()
				elif y < self.mouse.y:
					self.mouse.goUp()
				elif y > self.mouse.y:
					self.mouse.goDown()
			else:
				self.isBack = True

		#cell = self.mouse.mazeMap.getCell(self.mouse.x, self.mouse.y)
		#self.mapPainter.putRobotInCell(cell)

class StrategyTestGoStepEV3(Strategy):
	mouse = None
	progress = 0

	def __init__(self, mouse):
		self.mouse = mouse

	def checkFinished(self):
		return self.progress >= 1

	def go(self):
		self.progress = self.progress + 1
		self.mouse.senseWalls()
		print(self.mouse.getCurrentCell().getWhichIsWall())
		self.mouse.goLeft()
		self.mouse.senseWalls()
		print(self.mouse.getCurrentCell().getWhichIsWall())
		self.mouse.goRight()
		self.mouse.senseWalls()
		print(self.mouse.getCurrentCell().getWhichIsWall())
		self.mouse.goUp()
		self.mouse.senseWalls()
		print(self.mouse.getCurrentCell().getWhichIsWall())
		self.mouse.goDown()
		self.mouse.senseWalls()
		print(self.mouse.getCurrentCell().getWhichIsWall())
		sleep(1)

class StrategyTestInitEV3(Strategy):
	mouse = None
	flag = False

	def __init__(self, mouse):
		self.mouse = mouse

	def checkFinished(self):
		return self.flag

	def go(self):
		self.mouse.commandTranslator.motorController.gyreset()
		self.flag = True
		sleep(1)

class StrategyTestDFSDisplayEV3(Strategy):
	mouse = None
	isVisited = []
	path = []
	isBack = False

	def __init__(self, mouse):
		self.mouse = mouse
		self.isVisited = [[0 for i in range(self.mouse.mazeMap.width)] for j in range(self.mouse.mazeMap.height)]
		self.isVisited[self.mouse.x][self.mouse.y] = 1
		self.network = NetworkInterface()
		self.network.initSocket()

	def checkFinished(self):
		return self.isBack

	def go(self):
		self.mouse.senseWalls()
		#print(self.mouse.getCurrentCell().getWhichIsWall())
		sendData = {'x': self.mouse.x, 'y':self.mouse.y, 'up':self.mouse.canGoUp(), 'down':self.mouse.canGoDown(), 'left':self.mouse.canGoLeft(), 'right':self.mouse.canGoRight()}
		self.network.sendStringData(sendData)

		if self.mouse.canGoLeft() and not self.isVisited[self.mouse.x-1][self.mouse.y]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x-1][self.mouse.y] = 1
			self.mouse.goLeft()
		elif self.mouse.canGoUp() and not self.isVisited[self.mouse.x][self.mouse.y-1]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x][self.mouse.y-1] = 1
			self.mouse.goUp()
		elif self.mouse.canGoRight() and not self.isVisited[self.mouse.x+1][self.mouse.y]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x+1][self.mouse.y] = 1
			self.mouse.goRight()
		elif self.mouse.canGoDown() and not self.isVisited[self.mouse.x][self.mouse.y+1]:
			self.path.append([self.mouse.x, self.mouse.y])
			self.isVisited[self.mouse.x][self.mouse.y+1] = 1
			self.mouse.goDown()
		else:
			if len(self.path) != 0:
				x, y = self.path.pop()
				if x < self.mouse.x:
					self.mouse.goLeft()
				elif x > self.mouse.x:
					self.mouse.goRight()
				elif y < self.mouse.y:
					self.mouse.goUp()
				elif y > self.mouse.y:
					self.mouse.goDown()
			else:
				self.isBack = True

class StrategyTestRendezvous(Strategy):
	mouse = None
	network = None
	finished = False
	numNeighbors = 0
	neighborInfo = {}
	centroid = []
	group = []
	groupCentroid = []
	weights = []
	visited = []
	path = []

	def __init__(self, mouse, numNeighbors, initLocations):
		self.weights = [0,0,0,0]
		self.centroid = [-1,-1]
		self.groupCentroid = [-1,-1]
		self.mouse = mouse
		self.numNeighbors = numNeighbors
		for key, value in initLocations.items():
			if key is not self.mouse.id:
				self.neighborInfo[key] = {'x':value[0], 'y':value[1], 'direction' : 'UP'}

		self.visited = [[-1 for i in range(self.mouse.mazeMap.width)] for j in range(self.mouse.mazeMap.height)]
		self.visited[self.mouse.x][self.mouse.y] = self.mouse.id
		self.network = NetworkInterface()
		self.network.initSocket()
		self.network.startReceiveThread()

	def checkFinished(self):
		return self.finished

	#determines if mouse is surrounded by walls
	#if it is it will move in that direction
	def checkFreedom(self):
		freedom = []
		if self.mouse.canGoLeft():
			freedom.append('left')
		if self.mouse.canGoRight():
			freedom.append('right')
		if self.mouse.canGoUp():
			freedom.append('up')
		if self.mouse.canGoDown():
			freedom.append('down')
		if len(freedom) is 1:
			#maybe append path?
			self.visited[self.mouse.x][self.mouse.y] = self.numNeighbors + 1
			if freedom[0] is 'left':
				self.visited[self.mouse.x-1][self.mouse.y] = self.mouse.id
				self.mouse.goLeft()
			elif freedom[0] is 'right':
				self.visited[self.mouse.x+1][self.mouse.y] = self.mouse.id
				self.mouse.goRight()
			elif freedom[0] is 'up':
				self.visited[self.mouse.x][self.mouse.y-1] = self.mouse.id
				self.mouse.goUp()
			elif freedom[0] is 'down':
				self.visited[self.mouse.x][self.mouse.y+1] = self.mouse.id
				self.mouse.goDown()
		return freedom

	#calculates global and if following anyone group centroids
	def calcCentroid(self):
		self.centroid = [self.mouse.x,self.mouse.y]
		for key, value in self.neighborInfo.items():
			self.centroid[0] += value['x']
			self.centroid[1] += value['y']
		self.centroid[0] = math.floor(self.centroid[0]/(self.numNeighbors + 1))
		self.centroid[1] = math.floor(self.centroid[1]/(self.numNeighbors + 1))

	def weightByCentroid(self, multiplier):
		x = self.centroid[0] - self.mouse.x
		y = self.centroid[1] - self.mouse.y
		distSq = (x*x) + (y*y)
		x *= distSq*multiplier
		y *= distSq*multiplier
		if x < 0:
			self.weights[0] += abs(x)
		else:
			self.weights[1] += x
		if y > 0:
			self.weights[2] += y
		else:
			self.weights[3] += abs(y)

	def calcGroupCentroid(self):
		if len(self.group) is 0: return
		self.groupCentroid = [self.mouse.x,self.mouse.y]
		for id in self.group.items():
			self.groupCentroid[0] += self.neighborInfo[id]['x']
			self.groupCentroid[1] += self.neighborInfo[id]['y']
		self.groupCentroid[0] = math.floor(self.groupCentroid[0]/(len(self.group) + 1))
		self.groupCentroid[1] = math.floor(self.groupCentroid[1]/(len(self.group) + 1))

	def weightByCentroid(self, multiplier):
		print('ehllo')

	#calculates weights based on neighbors distances
	def weightByNeighbor(self, multiplier):
		x = 0
		y = 0
		for key, value in self.neighborInfo.items():
			x = value['x'] - self.mouse.x
			y = value['y'] - self.mouse.y
			#dist squared
			distSq = (x*x) + (y*y)
			x *= distSq*multiplier
			y *= distSq*multiplier
			if x < 0:
				self.weights[0] += abs(x)
			else:
				self.weights[1] += x
			if y > 0:
				self.weights[2] += y
			else:
				self.weights[3] += abs(y)

	def go(self):
		self.mouse.senseWalls()
		print(self.mouse.getCurrentCell().getWhichIsWall())

		sendData = {'id': self.mouse.id, 'direction': self.mouse.direction,
		'x': self.mouse.x, 'y':self.mouse.y, 'up': not self.mouse.canGoUp(),
		'down': not self.mouse.canGoDown(), 'left': not self.mouse.canGoLeft(),
		'right': not self.mouse.canGoRight()}

		self.network.sendStringData(sendData)
		recvData = self.network.retrieveData()

		while recvData:
			otherMap = recvData
			cell = self.mouse.mazeMap.getCell(otherMap['x'], otherMap['y'])
			if self.visited[otherMap['x']][otherMap['y']] is not self.numNeighbors + 1:
				self.visited[otherMap['x']][otherMap['y']] = otherMap['id']
			if otherMap['id'] is not self.mouse.id:
				self.neighborInfo[otherMap['id']] = {'x':otherMap['x'], 'y':otherMap['y'],'direction':otherMap['direction']}
			if otherMap['up']: self.mouse.mazeMap.setCellUpAsWall(cell)
			if otherMap['down']: self.mouse.mazeMap.setCellDownAsWall(cell)
			if otherMap['left']: self.mouse.mazeMap.setCellLeftAsWall(cell)
			if otherMap['right']: self.mouse.mazeMap.setCellRightAsWall(cell)
			recvData = self.network.retrieveData()

		previousWeights = self.weights
		self.weights = [0,0,0,0]
		freedom = self.checkFreedom()
		if len(freedom) is 1: return

		self.calcCentroids()

		x = centroid[0] - self.mouse.x
		y = centroid[1] - self.mouse.x
		distSq = (x*x)+(y*y)
		dontMove = True
		for value in self.neighborInfo.values():
			x = centroid[0] - value['x']
			y = centroid[1] - value['y']
			if distSq >= (x*x)+(y*y):
				dontMove = False
				break
		if dontMove and len(self.group) is self.numNeighbors:
			print('closest centroid...waiting for neighbors to gain ground')
			return


		ranks = [('left',options[0]),('right',options[1]),('down',options[2]),('up',options[3])]
		ranks = sorted(ranks, key=itemgetter(1))


		#narrow region
		moved = False
		prevVisitor = -1
		self.path.append([self.mouse.x, self.mouse.y])
		for d in range(4):
			direction = ranks[3 - d][0]
			if self.mouse.canGoLeft() and direction is 'left':
				prevVisitor = self.visited[self.mouse.x-1][self.mouse.y];
				if prevVisitor is self.numNeighbors + 1: continue
				if prevVisitor is not self.mouse.id or freedom is 1:
					self.visited[self.mouse.x-1][self.mouse.y] = self.mouse.id
					self.mouse.goLeft()
					moved = True
			elif self.mouse.canGoUp() and direction is 'up':
				prevVisitor = self.visited[self.mouse.x][self.mouse.y-1]
				if prevVisitor is self.numNeighbors + 1: continue
				if prevVisitor is not self.mouse.id or freedom is 1:
					self.visited[self.mouse.x][self.mouse.y-1] = self.mouse.id
					self.mouse.goUp()
					moved = True
			elif self.mouse.canGoRight() and direction is 'right':
				prevVisitor = self.visited[self.mouse.x+1][self.mouse.y]
				if prevVisitor is self.numNeighbors + 1: continue
				if prevVisitor is not self.mouse.id or freedom is 1:
					self.visited[self.mouse.x+1][self.mouse.y] = self.mouse.id
					self.mouse.goRight()
					moved = True
			elif self.mouse.canGoDown() and direction is 'down':
				prevVisitor = self.visited[self.mouse.x][self.mouse.y+1]
				if prevVisitor is self.numNeighbors + 1: continue
				if prevVisitor is not self.mouse.id or freedom is 1:
					self.visited[self.mouse.x][self.mouse.y+1] = self.mouse.id
					self.mouse.goDown()
					moved = True
			if moved:
				if prevVisitor is not self.mouse.id and prevVisitor is not -1 and \
				prevVisitor is not self.numNeighbors + 1 and prevVisitor not in self.group:
					self.group.append(prevVisitor)
				break
		if not moved and len(self.path) != 0:
			x, y = self.path[-2]
			if len(self.path) > 10: self.path = self.path[1:]
			if x < self.mouse.x:
				self.mouse.goLeft()
			elif x > self.mouse.x:
				self.mouse.goRight()
			elif y < self.mouse.y:
				self.mouse.goUp()
			elif y > self.mouse.y:
				self.mouse.goDown()


		#once all within distance chose collective location and wall follow there
		#maybe label cells with cold and hot spots


		sleep(0.5)

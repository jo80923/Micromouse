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
	homeOwner = {}
	isLeader = False
	detectedStop = 0
	timeStep = 0.1

	def __init__(self, mouse, numNeighbors, initLocations):
		self.weights = [0,0,0,0]
		self.centroid = [-1,-1]
		self.groupCentroid = [-1,-1]
		self.stop = [-1,-1]
		self.mouse = mouse
		self.numNeighbors = numNeighbors
		for key, value in initLocations.items():
			if key is not self.mouse.id:
				self.neighborInfo[key] = {'x':value[0], 'y':value[1], 'direction' : 'UP'}
		if [self.mouse.x,self.mouse.y] is [0,0]: self.isLeader = True
		self.visited = [[-1 for i in range(self.mouse.mazeMap.width)] for j in range(self.mouse.mazeMap.height)]
		self.visited[self.mouse.x][self.mouse.y] = self.mouse.id
		self.network = NetworkInterface()
		self.network.initSocket()
		self.network.startReceiveThread()

	def checkFinished(self):
		x = 0
		y = 0
		self.finished = False
		if len(self.neighborInfo) is not self.numNeighbors:
			self.finished = False
			return self.finished
		for value in self.neighborInfo.values():
			x = value['x'] - self.mouse.x
			y = value['y'] - self.mouse.y
			if math.sqrt((x*x)+(y*y)) is 0.0:
				self.finished = False
				break
		return self.finished

	def isAtCentroid(self):
		x = self.mouse.x - self.centroid[0]
		y = self.mouse.y - self.centroid[1]
		if math.sqrt((x*x)+(y*y)) is 0.0:
			return True
		else: return False

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
			self.path.append([self.mouse.x, self.mouse.y])
			self.visited[self.mouse.x][self.mouse.y] = self.numNeighbors + 1
			if freedom[0] is 'left':
				self.visited[self.mouse.x-1][self.mouse.y] = self.mouse.id
				self.mouse.goLeft()
			elif freedom[0] is 'right':
				self.visited[self.mouse.x+1][self.mouse.y] = self.mouse.id
				self.mouse.goRight()
			elif freedom[0] == 'up':
				self.visited[self.mouse.x][self.mouse.y-1] = self.mouse.id
				self.mouse.goUp()
			elif freedom[0] is 'down':
				self.visited[self.mouse.x][self.mouse.y+1] = self.mouse.id
				self.mouse.goDown()
		return freedom

	#returns len(group)
	def refineGroup(self, threshold):
		if len(self.group) is 0: return False
		withinThreshold = True
		distSqNeighbors = 0
		for item in self.group:
			x = self.neighborInfo[item]['x'] - self.mouse.x
			y = self.neighborInfo[item]['y'] - self.mouse.y
			distSqNeighbors = (x*x)+(y*y)
			if distSqNeighbors > threshold*threshold:
				self.group.remove(item)
		return len(self.group)

	#returns true if all bots within threshold and removes bots outside maxDist
	def checkGroupDist(self, distance):
		withinThreshold = True
		distSqNeighbors = 0
		for item in self.group:
			x = self.neighborInfo[item]['x'] - self.mouse.x
			y = self.neighborInfo[item]['y'] - self.mouse.y
			distSqNeighbors = (x*x)+(y*y)
			if distSqNeighbors > distance*distance:
				withinThreshold = False
				break

		return withinThreshold

	#returns max distance squared of group member to group centroid
	def calcMaxDistFromGroupCentroid(self):
		if len(self.group) is 0 or self.groupCentroid is [-1,-1]:
			return sys.maxsize
		x = self.groupCentroid[0] - self.mouse.x
		y = self.groupCentroid[1] - self.mouse.y
		distSq = (x*x) + (y*y)
		maxDist = distSq
		for item in self.group:
			x = self.groupCentroid[0] - self.neighborInfo[item]['x']
			y = self.groupCentroid[1] - self.neighborInfo[item]['y']
			distSq = (x*x)+(y*y)
			if distSq > maxDist: distSq = maxDist
		return maxDist

	#returns max distance squared of member to centroid
	def calcMaxDistFromCentroid(self):
		if len(self.neighborInfo) < self.numNeighbors or self.centroid is [-1,-1]:
			return sys.maxsize
		x = self.centroid[0] - self.mouse.x
		y = self.centroid[1] - self.mouse.y
		distSq = (x*x) + (y*y)
		maxDist = distSq
		for value in self.neighborInfo.values():
			x = self.centroid[0] - value[item]['x']
			y = self.centroid[1] - value[item]['y']
			distSq = (x*x)+(y*y)
			if distSq > maxDist: distSq = maxDist
		return maxDist

	#returns true if closest to centroid
	def isClosestToGroupCentroid(self):
		if len(self.group) is 0 or self.groupCentroid is [-1,-1]:
			return sys.maxsize
		x = self.groupCentroid[0] - self.mouse.x
		y = self.groupCentroid[1] - self.mouse.y
		distSq = (x*x) + (y*y)
		currentValue = distSq
		isClosest = True
		for item in self.group:
			x = self.groupCentroid[0] - self.neighborInfo[item]['x']
			y = self.groupCentroid[1] - self.neighborInfo[item]['y']
			distSq = (x*x)+(y*y)
			if distSq < currentValue:
				isClosest = False
				break
		return isClosest

	#returns true if closest to group centroid
	def isClosestToCentroid(self):
		if len(self.neighborInfo) < self.numNeighbors or self.centroid is [-1,-1]:
			return False
		x = self.centroid[0] - self.mouse.x
		y = self.centroid[1] - self.mouse.y
		distSq = (x*x) + (y*y)
		currentValue = distSq
		isClosest = True
		for value in self.neighborInfo.values():
			x = self.centroid[0] - value[item]['x']
			y = self.centroid[1] - value[item]['y']
			distSq = (x*x)+(y*y)
			if distSq <= currentValue:
				isClosest = False
				break
		return isClosest

	#returns true if closest to group centroid and all within threshold
	def checkClosenessToGroupCentroid(self, threshold):
		if len(self.group) is 0 or self.groupCentroid is [-1,-1]:
			return sys.maxsize
		x = self.groupCentroid[0] - self.mouse.x
		y = self.groupCentroid[1] - self.mouse.y
		distSq = (x*x) + (y*y)
		currentValue = distSq
		if currentValue > threshold*threshold:
			return False
		isClosest = True
		for item in self.group:
			x = self.groupCentroid[0] - self.neighborInfo[item]['x']
			y = self.groupCentroid[1] - self.neighborInfo[item]['y']
			distSq = (x*x)+(y*y)
			if distSq < currentValue or distSq > threshold*threshold:
				isClosest = False
				break
		return isClosest

	#returns true if closest to centroid and all within threshold
	def checkClosenessToCentroid(self, threshold):
		if len(self.neighborInfo) < self.numNeighbors or self.centroid is [-1,-1]:
			return False
		x = self.centroid[0] - self.mouse.x
		y = self.centroid[1] - self.mouse.y
		distSq = (x*x) + (y*y)
		currentValue = distSq
		if currentValue > threshold*threshold:
			return False
		isClosest = True
		for value in self.neighborInfo.values():
			x = self.centroid[0] - value[item]['x']
			y = self.centroid[1] - value[item]['y']
			distSq = (x*x)+(y*y)
			if distSq <= currentValue or distSq > threshold*threshold:
				isClosest = False
				break
		return isClosest

	#returns true if all bots within threshold and removes bots outside maxDist
	def refineAndCheckGroupDist(self, threshold, distance):
		withinThreshold = True
		distSqNeighbors = 0
		for item in self.group:
			x = self.neighborInfo[item]['x'] - self.mouse.x
			y = self.neighborInfo[item]['y'] - self.mouse.y
			distSqNeighbors = (x*x)+(y*y)
			if distSqNeighbors > threshold*threshold:
				self.group.remove(item)
			if distSqNeighbors > distance*distance:
				withinThreshold = False

		return withinThreshold

	#calculates global and if following anyone group centroids
	def calcCentroid(self):
		self.centroid = [self.mouse.x,self.mouse.y]
		for key, value in self.neighborInfo.items():
			self.centroid[0] += value['x']
			self.centroid[1] += value['y']
		self.centroid[0] = math.floor(self.centroid[0]/(self.numNeighbors + 1))
		self.centroid[1] = math.floor(self.centroid[1]/(self.numNeighbors + 1))

	def weightByXY(self, x, y, multiplier):
		if multiplier is 0: return
		xDir = x - self.mouse.x
		yDir = y - self.mouse.y
		distSq = (xDir*xDir) + (yDir*yDir)
		xDir *= distSq*multiplier
		yDir *= distSq*multiplier
		if xDir < 0:
			self.weights[0] += abs(xDir)
		else:
			self.weights[1] += xDir
		if yDir > 0:
			self.weights[2] += yDir
		else:
			self.weights[3] += abs(yDir)

	def weightByCentroid(self, multiplier):
		if multiplier is 0: return
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
		for id in self.group:
			self.groupCentroid[0] += self.neighborInfo[id]['x']
			self.groupCentroid[1] += self.neighborInfo[id]['y']
		self.groupCentroid[0] = math.floor(self.groupCentroid[0]/(len(self.group) + 1))
		self.groupCentroid[1] = math.floor(self.groupCentroid[1]/(len(self.group) + 1))

	def weightByGroup(self, multiplier):
		if multiplier is 0: return
		x = self.groupCentroid[0] - self.mouse.x
		y = self.groupCentroid[1] - self.mouse.y
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

	#calculates weights based on neighbors distances
	def weightByNeighbor(self, multiplier):
		if multiplier is 0: return
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

		numPackets = 0
		prevLocal = [0,0]
		stop = [-1,-1]
		#NOTE think if more than one in same spot

		while recvData:
			otherMap = recvData
			cell = self.mouse.mazeMap.getCell(otherMap['x'], otherMap['y'])
			if self.visited[otherMap['x']][otherMap['y']] is not self.numNeighbors + 1:
				self.visited[otherMap['x']][otherMap['y']] = otherMap['id']
			if otherMap['id'] in self.neighborInfo:
				prevLocal = [self.neighborInfo[otherMap['id']]['x'],self.neighborInfo[otherMap['id']]['y']]
				self.neighborInfo[otherMap['id']] = {'x':otherMap['x'], 'y':otherMap['y'],'direction':otherMap['direction']}
				numPackets += 1
				if prevLocal is [otherMap['x'],otherMap['y']]:
					stop = prevLocal

			if otherMap['up']: self.mouse.mazeMap.setCellUpAsWall(cell)
			if otherMap['down']: self.mouse.mazeMap.setCellDownAsWall(cell)
			if otherMap['left']: self.mouse.mazeMap.setCellLeftAsWall(cell)
			if otherMap['right']: self.mouse.mazeMap.setCellRightAsWall(cell)
			recvData = self.network.retrieveData()

		#if numPackets < 3 and self.centroid is not [-1,-1]:
		#	print('error numPackets should be 3 but is ')
		#	print(numPackets)
		#	sys.exit(1)

		if stop is not [-1,-1]:
			self.centroid = stop
			self.groupCentroid = stop
		else:
			self.calcCentroid()
			self.calcGroupCentroid()

		freedom = []
		freedom = self.checkFreedom()
		if len(freedom) is 1 or self.isAtCentroid():
			sleep(0.1)
			return

		previousWeights = self.weights
		self.weights = [0,0,0,0]
		groupWeight = 0
		centroidWeight = 0
		neighborWeight = 0
		groupSize = self.refineGroup(8)

		centroidWeight = 1
		neighborWeight = (self.numNeighbors  + 1 - len(self.group))
		if len(self.group) > 0:
			groupWeight = len(self.group)

		if groupSize is self.numNeighbors:
			if stop is [-1,-1] and self.isClosestToCentroid():
				sleep(0.1)
				return
			centroidWeight *= (groupWeight+neighborWeight)


		self.weightByNeighbor(neighborWeight)
		self.weightByCentroid(centroidWeight)
		self.weightByGroup(groupWeight)

		ranks = [('left',self.weights[0]),('right',self.weights[1]),('down',self.weights[2]),('up',self.weights[3])]
		ranks = sorted(ranks, key=itemgetter(1))
		moved = False
		for d in range(4):
			direction = ranks[3 - d][0]
			if direction not in freedom: continue
			if direction is 'left':
				prevVisitor = self.visited[self.mouse.x-1][self.mouse.y];
				if prevVisitor is self.numNeighbors + 1: continue
				if prevVisitor is not self.mouse.id:# or (previousWeights[0] >= self.weights[0] and len(self.path) < 30):
					self.path.append([self.mouse.x, self.mouse.y])
					self.visited[self.mouse.x-1][self.mouse.y] = self.mouse.id
					self.mouse.goLeft()
					moved = True
			elif direction is 'up':
				prevVisitor = self.visited[self.mouse.x][self.mouse.y-1]
				if prevVisitor is self.numNeighbors + 1: continue
				if prevVisitor is not self.mouse.id:# or (previousWeights[3] >= self.weights[3] and len(self.path) < 30):
					self.path.append([self.mouse.x, self.mouse.y])
					self.visited[self.mouse.x][self.mouse.y-1] = self.mouse.id
					self.mouse.goUp()
					moved = True
			elif direction is 'right':
				prevVisitor = self.visited[self.mouse.x+1][self.mouse.y]
				if prevVisitor is self.numNeighbors + 1: continue
				if prevVisitor is not self.mouse.id:# or (previousWeights[1] >= self.weights[1] and len(self.path) < 30):
					self.path.append([self.mouse.x, self.mouse.y])
					self.visited[self.mouse.x+1][self.mouse.y] = self.mouse.id
					self.mouse.goRight()
					moved = True
			elif direction is 'down':
				prevVisitor = self.visited[self.mouse.x][self.mouse.y+1]
				if prevVisitor is self.numNeighbors + 1: continue
				if prevVisitor is not self.mouse.id:# or (previousWeights[2] >= self.weights[2] and len(self.path) < 30):
					self.path.append([self.mouse.x, self.mouse.y])
					self.visited[self.mouse.x][self.mouse.y+1] = self.mouse.id
					self.mouse.goDown()
					moved = True
			if moved:
				if prevVisitor is not self.mouse.id and prevVisitor is not -1 and \
				prevVisitor is not self.numNeighbors + 1 and prevVisitor not in self.group:
					self.group.append(prevVisitor)
				break
		if not moved and len(self.path) != 0:
			#xp, yp = self.path[-1]
			#if self.visited[xp][yp] is self.numNeighbors + 1:
			#	self.path.pop()
			#	xp,yp = self.path[-1]
			xp, yp = self.path.pop()
			if self.visited[xp][yp] is self.numNeighbors + 1:
				xp, yp = self.path.pop()
			if xp < self.mouse.x:
				self.mouse.goLeft()
			elif xp > self.mouse.x:
				self.mouse.goRight()
			elif yp < self.mouse.y:
				self.mouse.goUp()
			elif yp > self.mouse.y:
				self.mouse.goDown()

		if len(self.path) > 10: self.path = self.path[1:]

		sleep(0.1)

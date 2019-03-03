#!/usr/bin/env python3

#Author: Zhiwei Luo

from task import Strategy, NetworkInterface
from time import sleep
import math
from operator import itemgetter

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
	visited = []
	path = []
	isBack = False
	network = None
	numNeighbors = 0
	neighborInfo = {}
	follow = []
	finished = False
	finalCentroid = []


	def __init__(self, mouse, numNeighbors, initLocations):
		self.mouse = mouse
		self.finalCentroid = [-1,-1]
		self.numNeighbors = numNeighbors
		for key, value in initLocations.items():
			if key is not self.mouse.id:
				self.neighborInfo[key] = {'x':value[0], 'y':value[1], 'direction' : 'UP'}

		self.visited = [[-1 for i in range(self.mouse.mazeMap.width)] for j in range(self.mouse.mazeMap.height)]
		self.visited[self.mouse.x][self.mouse.y] = 1
		self.network = NetworkInterface()
		self.network.initSocket()
		self.network.startReceiveThread()

	def checkFinished(self):
		return self.isBack

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

		x = 0
		y = 0
		options = [0, 0, 0, 0]
		self.finished = True
		found = 0
		#calc centroid and weights
		centroid = [self.mouse.x,self.mouse.y]
		for key, value in self.neighborInfo.items():
			centroid[0] += value['x']
			centroid[1] += value['y']
			x = value['x'] - self.mouse.x
			y = value['y'] - self.mouse.y
			#dist squared
			dist = math.sqrt((x*x) + (y*y))
			if dist is not 0.0: self.finished = False
			if dist <= 2.0:
				if key not in self.follow:
					self.follow.append(key)
				found += 1
			elif dist > 4.0 and key in self.follow:
				self.follow.remove(key)
			x *= int(dist)
			y *= int(dist)
			if x < 0:
				options[0] += abs(x)
			else:
				options[2] += x
			if y > 0:
				options[1] += y
			else:
				options[3] += abs(y)

		if self.finished: return
		centroid[0] /= self.numNeighbors + 1
		centroid[1] /= self.numNeighbors + 1

		isLeader = False
		#TODO implement check if leader
		i = 0
		#if found >= self.numNeighbors - 1:
		#	isLeader = True
		#	for key, value in self.neighborInfo.items():
		#		if key < self.mouse.id and distances[i] <= 2.0:
		#			isLeader = False
		#			break
		#		i += 1

		moved = False
		freedom = 0
		if self.mouse.canGoLeft(): freedom += 1
		if self.mouse.canGoRight(): freedom += 1
		if self.mouse.canGoUp(): freedom += 1
		if self.mouse.canGoDown(): freedom += 1
		if freedom is 1:
			self.visited[self.mouse.x][self.mouse.y] = self.numNeighbors + 1

		x = centroid[0] - self.mouse.x
		y = centroid[1] - self.mouse.x
		dist = math.sqrt((x*x)+(y*y))
		maxDistFromCentroid = dist
		if self.finalCentroid is not [-1,-1]:
			centroid = self.finalCentroid
		else:
			for value in self.neighborInfo.values():
				x = centroid[0] - value['x']
				y = centroid[1] - value['y']
				dist = math.sqrt((x*x)+(y*y))
				if dist > maxDistFromCentroid:
					maxDistFromCentroid = dist
			if maxDistFromCentroid < 8.0:
				self.finalCentroid = centroid
			x = centroid[0] - self.mouse.x
			y = centroid[1] - self.mouse.x
			dist = math.sqrt((x*x) + (y*y))
		if dist < 8.0:
			if x < 0:
				options[0] += abs(x)#*int(dist)
			else:
				options[1] += x#*int(dist)
			if y > 0:
				options[2] += y#*int(dist)
			else:
				options[3] += abs(y)#*int(dist)

		ranks = [('left',options[0]),('right',options[1]),('down',options[2]),('up',options[3])]
		ranks = sorted(ranks, key=itemgetter(1))
		#if within distance of a centroid then chasing centroid else narrow region
		#this could be done by making the input values for ranks different or
		#making DFS towards centroid

		#narrow region
		for d in range(4):
			direction = ranks[3 - d][0]
			if self.mouse.canGoLeft() and direction is 'left' and\
			(self.visited[self.mouse.x-1][self.mouse.y] is not self.mouse.id or
			self.visited[self.mouse.x-1][self.mouse.y] in self.follow) and\
			self.visited[self.mouse.x-1][self.mouse.y] is not self.numNeighbors + 1:
				self.path.append([self.mouse.x, self.mouse.y])
				self.visited[self.mouse.x-1][self.mouse.y] = self.mouse.id
				self.mouse.goLeft()
				moved = True
			elif self.mouse.canGoUp() and direction is 'up' and\
			(self.visited[self.mouse.x][self.mouse.y-1] is not self.mouse.id or
			self.visited[self.mouse.x][self.mouse.y-1] in self.follow) and\
			self.visited[self.mouse.x][self.mouse.y-1] is not self.numNeighbors + 1:
				self.path.append([self.mouse.x, self.mouse.y])
				self.visited[self.mouse.x][self.mouse.y-1] = self.mouse.id
				self.mouse.goUp()
				moved = True
			elif self.mouse.canGoRight() and direction is 'right' and\
			(self.visited[self.mouse.x+1][self.mouse.y] is not self.mouse.id or
			self.visited[self.mouse.x+1][self.mouse.y] in self.follow) and\
			self.visited[self.mouse.x+1][self.mouse.y] is not self.numNeighbors + 1:
				self.path.append([self.mouse.x, self.mouse.y])
				self.visited[self.mouse.x+1][self.mouse.y] = self.mouse.id
				self.mouse.goRight()
				moved = True
			elif self.mouse.canGoDown() and direction is 'down' and\
			(self.visited[self.mouse.x][self.mouse.y+1] is not self.mouse.id or
			self.visited[self.mouse.x][self.mouse.y+1] in self.follow) and\
			self.visited[self.mouse.x][self.mouse.y+1] is not self.numNeighbors + 1:
				self.path.append([self.mouse.x, self.mouse.y])
				self.visited[self.mouse.x][self.mouse.y+1] = self.mouse.id
				self.mouse.goDown()
				moved = True
			if moved: break
		if not moved and len(self.path) != 0:
			x, y = self.path.pop()
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


		sleep(0.25)

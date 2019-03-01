#!/usr/bin/env python3

#Author: Zhiwei Luo

from map import Map
from mouse import Micromouse
from strategy import StrategyTestRendezvous
from controller import COREController
from socket import *

mazeMap = Map(16, 16)
totalMice = 4
mazeMap.readFromFile('/home/jackson/Development/Micromouse/mazes/2012japan-ef.txt')
id = gethostname()[1:]
micromouse = Micromouse(mazeMap, id)
initPoint = {'1':(0,0), '2':(15,0), '3':(0,15), '4':(15,15)}
micromouse.setMotorController(COREController(id, initPoint[id], '10.0.0.254'))
micromouse.setInitPoint(initPoint[id][0], initPoint[id][1])
micromouse.addTask(StrategyTestRendezvous(micromouse, totalMice - 1, initPoint))#minus one as this is numNeighbors
micromouse.run()

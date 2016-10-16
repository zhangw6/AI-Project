# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for 
# educational purposes provided that (1) you do not distribute or publish 
# solutions, (2) you retain this notice, and (3) you provide clear 
# attribution to UC Berkeley, including a link to 
# http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero 
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and 
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

from captureAgents import CaptureAgent
import random, time, util, operator
from util import nearestPoint
from game import Directions,Actions
import game

POWERCAPSULETIME = 120

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'FullTimeAttackAgent', second = 'PartTimeDefenseAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.
  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]


class MainAgent(CaptureAgent):

  
  def __init__(self, gameState):
    CaptureAgent.__init__(self, gameState)
    self.mostlikely = [None]*4
    self.powerTimer = 0
  
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)

    if self.red:
      CaptureAgent.registerTeam(self, gameState.getRedTeamIndices())
    else:
      CaptureAgent.registerTeam(self, gameState.getBlueTeamIndices())
    self.width, self.height = gameState.getWalls().asList()[-1] 
    self.legalPositions = [p for p in gameState.getWalls().asList(False) if p[1] > 1]
    self.walls = list(gameState.getWalls())

    if self.red:
        offset = -3
    else:
        offset = 4
    
    self.chokes = []
    for a in range(self.height): 
        if not self.walls[self.width/2+offset][a]:
            self.chokes.append(((self.width/2+offset), a))  
    if self.index == max(gameState.getRedTeamIndices()) or self.index == max(gameState.getBlueTeamIndices()):
        h, v = self.chokes[3*len(self.chokes)/4]
    else:
        h, v = self.chokes[1*len(self.chokes)/4]
    self.goal = (h, v) 

    global beliefs
    beliefs = [util.Counter()] * gameState.getNumAgents() 
    
    
    for i, val in enumerate(beliefs):
        if i in self.getOpponents(gameState): 
            beliefs[i][gameState.getInitialAgentPosition(i)] = 1.0  
      
    
    self.goMid(gameState)
  def otherAgentD(self, gameState):
    dist = None
    agentsList = self.agentsOnTeam
    if self.index == self.agentsOnTeam[0]:
      ob = self.agentsOnTeam[1]
      dista = None
    else:
      ob = self.agentsOnTeam[0]
      myPos = self.MyPos(gameState)
      obPos = gameState.getAgentState(ob).getPosition()
      dist = self.getMazeDistance(myPos, obPos)
      if dist == 0:
        dist = 0.5
    return dist
  
  def oppoDist(self, gameState):
    pos = self.getClosestOpntPos(gameState)
    minD= None
    if len(pos) > 0:
      minD = 99999999999.0
      myP = gameState.getAgentPosition(self.index)
      for e, p in pos:
        d = self.getMazeDistance(p, myP)
        if d < minD:
          minD = d
    return minD
  def getClosestOpntPos(self, gameState):
    ep = []
    for e in self.getOpponents(gameState):
      p = gameState.getAgentPosition(e)
      if p != None:
        ep.append((e, p))
    return ep

  def ifPac(self, gameState):
    return gameState.getAgentState(self.index).isPacman
  
 
  def MyPos(self, gameState):
    return gameState.getAgentState(self.index).getPosition()

  
    
  def side(self,gameState):
    width, v = gameState.data.layout.width, gameState.data.layout.height
    pos = gameState.getAgentPosition(self.index)
    if self.index%2==1:
      
      if pos[0]<width/(2):
        return 1.0
      else:
        return 0.0
    else:
      
      if pos[0]>width/2-1:
        return 1.0
      else:
        return 0.0

  def powerful(self):
    return self.powerTimer > 0
  
  def ScaredTimer(self, gameState):
    return gameState.getAgentState(self.index).scaredTimer

  def getDist(self, pos):
    px = [pos[0],pos[0]-1,pos[0+1],pos[0],pos[0]]
    py = [pos[1]-1,pos[1],pos[1],pos[1]+1,pos[-1]]
    posActions = zip(px,py)
    actions = []
    for act in posActions:
        if act in self.legalPositions:
            actions.append(act)
        
    dist = util.Counter()
    for act in actions:
        dist[act] = 1
    return dist
        
  
  def elapseTime(self, gameState): 
    for agent, belief in enumerate(beliefs):
        if agent in self.getOpponents(gameState):
            newBeliefs = util.Counter()
            
            pos = gameState.getAgentPosition(agent) 
            if pos != None:
                newBeliefs[pos] = 1.0
            else:
                
                for p in belief:
                    if p in self.legalPositions and belief[p] > 0: 
                       
                        newPosDist = self.getDist(p)
                        for x, y in newPosDist:
                            newBeliefs[x, y] += belief[p] * newPosDist[x, y] 
                           
                if len(newBeliefs) == 0:
                    oldState = self.getPreviousObservation()
                    if oldState != None and oldState.getAgentPosition(agent) != None:
                        newBeliefs[oldState.getInitialAgentPosition(agent)] = 1.0
                    else:
                        for p in self.legalPositions: newBeliefs[p] = 1.0
            beliefs[agent] = newBeliefs

  def observe(self, agent, noisyDistance, gameState):
    myPos = gameState.getAgentPosition(self.index)
        
    allPossible = util.Counter()
    for p in self.legalPositions:  
      trueDistance = util.manhattanDistance(p, myPos) 
      allPossible[p] += gameState.getDistanceProb(trueDistance, noisyDistance)  
    for p in self.legalPositions:
      beliefs[agent][p] *= allPossible[p]  
    
  def chooseAction(self, gameState):
    
    actions = gameState.getLegalActions(self.index)
    
    opponents = self.getOpponents(gameState)
    noisyD = gameState.getAgentDistances() 
    myPos = gameState.getAgentPosition(self.index)
    for agent in opponents:
        self.observe(agent, noisyD[agent], gameState) 
   
    self.locations = [self.chokes[len(self.chokes)/2]] * gameState.getNumAgents() 
    for i, belief in enumerate(beliefs):
        maxl = 0
        allMaybe = 0
        for v in beliefs[i]:
   
            if belief[v] == maxl and maxl > 0: 
                
                allMaybe += 1 
            elif belief[v] > maxl:
                maxl = belief[v]
                self.locations[i] = v
        if allMaybe > 5:
            self.locations[i] = self.goal
   
    
    for agent in opponents:
        beliefs[agent].normalize()   
        self.mostlikely[agent] = max(beliefs[agent].iteritems(), key=operator.itemgetter(1))[0]
    
    self.elapseTime(gameState)
    agentPos = gameState.getAgentPosition(self.index)
    mode = 'attack' 

    if self.atCenter == False :
      mode = 'start'

   
    if agentPos == self.center and self.atCenter == False :
      self.atCenter = True
      mode = 'attack'
    for agent in opponents:
        if(gameState.getAgentState(agent).isPacman and ((self.index == 2) or (self.index == 3)) ):
            mode = 'defend'    
    
    actions = gameState.getLegalActions(self.index)
    values = [self.evaluate(gameState, a, mode) for a in actions]

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
  
    return random.choice(bestActions)


  def getSuccessor(self, gameState, action):
    
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action, mode):
    
    if mode == 'attack':
     
      features = self.getFeaturesAttack(gameState, action)
      weights = self.getWeightsAttack(gameState, action)
    elif mode == 'defend':
      
      features = self.getFeaturesDefend(gameState, action)
      weights = self.getWeightsDefend(gameState, action)
    elif mode == 'start':
      features = self.getFeaturesStart(gameState, action)
      weights = self.getWeightsStart(gameState, action)

    return features * weights

    
  def getFeaturesAttack(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    agentsList = self.agentsOnTeam
    width = gameState.data.layout.width
    height = gameState.data.layout.height
    foodList = self.getFood(successor).asList()

    
    features['successorScore'] = self.getScore(successor)

    
    if len(foodList) > 0:

      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distFood'] = minDistance
    
    if(len(foodList)>0):
      features['getFood'] = -len(foodList) +self.getScore(successor)
    
    myPosLeft = ()
    myPosDown = ()
    myPosUp = ()
    myPosRight = ()

    walls = gameState.getWalls().asList(True)

    myPosLeft = ()
    myPosDown = ()
    myPosUp = ()
    myPosRight = ()
    numOfWall = 0

    walls = gameState.getWalls().asList()

    if self.ifPac(gameState) and ((self.index == 1) or (self.index == 0))  :
  

       x,y = myPos
       myPosUp = (x,y+1)
       myPosDown = (x,y-1)
       myPosLeft = (x-1,y)
       myPosRight = (x+1,y)

       # around = [myPosUp,myPosRight,myPosLeft,myPosDown]
      
    for pos in [myPosUp,myPosRight,myPosLeft,myPosDown]:
      if pos in walls:
        numOfWall += numOfWall
    if numOfWall == 3:
      features['threeWalls'] = -1
    else:
      features['threeWalls'] = 1

    
   
    distEnemy = self.oppoDist(successor)
    if(distEnemy != None):
       if(distEnemy <= 2):
         features['closeG'] = 4/distEnemy
       elif(distEnemy <= 4):
          features['closeG'] = 1
       else:
          features['closeG'] = 0  
    capsules = self.getCapsules(successor)
    if(len(capsules) > 0):
      mincapdist = min([self.getMazeDistance(myPos, capsule) for capsule in capsules])
      features['pickcap'] = -len(capsules)
    else:
      mincapdist = .1
    features['capdist'] =  1.0/mincapdist

    
    if myPos in self.getFood(gameState).asList():
      self.foodNum += 1.0
    if self.side(gameState) == 0.0:
      self.foodNum = 0.0
    features['hold'] = self.foodNum*(min([self.distancer.getDistance(myPos,p) for p in [(width/2,i) for i in range(1,height) if not gameState.hasWall(width/2,i)]]))*self.side(gameState)          
    
    features['drop'] = self.foodNum*(self.side(gameState))
    
    if myPos in self.getCapsules(gameState):
        self.powerTimer = POWERCAPSULETIME
    
    if self.powerTimer>0:
        self.powerTimer -= 1
    
    if(self.powerful()):

      features['powerful'] = self.powerTimer
      # features['hold'] = 0.0
      features['getFood'] = 100*features['getFood']
    else:
      features['powerful'] = 0.0
    
    
    if self.ifPac(successor):
      distanceToAlly = self.otherAgentD(successor)
     
      if distanceToAlly != None:
        features['distPart'] = 1.0/distanceToAlly
    
    
    actions = gameState.getLegalActions(self.index)
    if(len(actions) <= 2):
       features['end'] = 1.0
    else:
       features['end'] = 0.0

    if(action == Directions.STOP):
       features['stop'] = 1.0
    else:
       features['stop'] = 0.0

    return features

   
  def getFeaturesDefend(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    
    walls = gameState.getWalls()
    x, y = gameState.getAgentState(self.index).getPosition()
    dx, dy = Actions.directionToVector(action)
    nextx = int(x + dx)
    nexty = int(y + dy)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [enemy for enemy in enemies if enemy.isPacman and enemy.getPosition() != None]
    


    if gameState.getAgentState(self.index).scaredTimer == 0:   
        ghostpos = myPos
        neighbors = Actions.getLegalNeighbors(ghostpos, walls)
        if (nextx, nexty) == ghostpos:
          features["kill"] = 1000
        elif (nextx, nexty) in neighbors:
          features["around"] += 1000
    else:
        if myPos!= None:
          ghostpos = myPos
          neighbors = Actions.getLegalNeighbors(ghostpos, walls)
          if (nextx, nexty) in neighbors:
            features["around"] += -10000
            features["kill"] = -10000
          elif (nextx, nexty) == ghostpos:
            features["kill"] = -10000
 
    features['numE'] = len(invaders)
    if len(invaders) > 0:
      enemyDist = [self.getMazeDistance(myPos, enemy.getPosition()) for enemy in invaders]
      
      features['Edist'] = min(enemyDist)
    

  
    distEnemy = self.oppoDist(successor)
  

    if(distEnemy <= 5):
      features['closeG'] = 1
      if(distEnemy <= 1 and self.ScaredTimer(successor) > 0):
        features['closeG'] = -1
    else:
      features['closeG'] = 0  
    

    if self.ifPac(successor):
      distanceToAlly = self.otherAgentD(successor)
      
      if distanceToAlly != None:
        features['distPart'] = 1.0/distanceToAlly

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['rev'] = 1

    return features

  def getFeaturesStart(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    dist = self.getMazeDistance(myPos, self.center)
    features['distToCenter'] = dist
    if myPos == self.center:
      features['atCenter'] = 1
    return features
  

  
  def getWeightsStart(self, gameState, action):
    return {'distToCenter': -1, 'atCenter': 1000}
  def getWeightsDefend(self, gameState, action):
    return {'numE': -1000, 'Edist': -50, 'stop': -500,
            'rev': -20, 'closeG': 300, 'distPart': -400,'kill':1000,'around':0}  

  
class FullTimeAttackAgent(MainAgent):

  def goMid(self, gameState):
    locations = []
    self.atCenter = False
    x = gameState.getWalls().width / 2
    y = gameState.getWalls().height / 2

    if self.red:
      x = x - 1
    
    self.center = (x, y)
    maxHeight = gameState.getWalls().height

   
    for i in xrange(maxHeight - y):
      if not gameState.hasWall(x, y):
        locations.append((x, y))
      y = y + 1

    myPos = gameState.getAgentState(self.index).getPosition()
    minDist = float('inf')
    minPos = None

    
    for location in locations:
      dist = self.getMazeDistance(myPos, location)
      if dist <= minDist:
        minDist = dist
        minPos = location
    
    self.center = minPos
  def getWeightsAttack(self, gameState, action): 
    return {'successorScore': 80, 'distFood': -1, 'closeG': -100,
            'getFood': 400, 'capdist': 70, 'stop': -100, 'end': -20,
            'powerful': 500000, 'drop': 10, 'hold': -2,
            'notTooClose': -600, 'pickcap': 500,'threeWalls':30}

class PartTimeDefenseAgent(MainAgent):

  def goMid(self, gameState):
    locations = []
    self.atCenter = False
    x = gameState.getWalls().width / 2
    y = gameState.getWalls().height / 2
   
    if self.red:
      x = x - 1
    

    if self.red:
     x = gameState.getWalls().width/4
    else:
     x = 3*gameState.getWalls().width/4
    self.center = (x, y)
    
    
    for i in xrange(y):
      if not gameState.hasWall(x, y):
        locations.append((x, y))
      y = y - 1

    myPos = gameState.getAgentState(self.index).getPosition()
    minDist = float('inf')
    minPos = None
    for location in locations:
      dist = self.getMazeDistance(myPos, location)
      if dist <= minDist:
        minDist = dist
        minPos = location
    
    self.center = minPos
  def getWeightsAttack(self, gameState, action): 
    return {'successorScore': 80, 'distFood': -1, 'closeG': -150,
            'getFood': 300, 'capdist': 70, 'stop': -100, 'end': -20,
            'powerful': 500000, 'drop': 20, 'hold': -5,
            'notTooClose': -600, 'pickcap': 200,'threeWalls':30}
 
  
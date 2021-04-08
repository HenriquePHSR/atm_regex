import pandas as pd
from tabulate import tabulate
import pprint
#import pygraphviz as pgv
from graphviz import Digraph


def countParent(er):
  count=0
  for char in er:
    if char == '(':
      count = count+1
  return count

def generateBaseAutomaton(var):
  sigma =  [var]
  Q = [var+"q0", var+"qf"]
  init = [var+"q0"]
  F = [var+"qf"]
  delta = {
      var+"q0" : {var : [var+"qf"]},
      var+"qf" : {}  
  }

  M = automaton(sigma, Q, delta, init, F)
  return M

def sumAutomaton(aut1, aut2):
  sigma = list(set(aut1.sigma + aut2.sigma + ['ɛ']))
  init = [aut1.init[0][:-2]+aut2.init[0][:-2]+'q0']
  F = [aut1.init[0][:-2]+aut2.init[0][:-2]+'qf']
  Q = list(set(aut1.Q + aut2.Q + init + F))
  
  tempF={}
  for final in aut1.F:
    tempF[final] = {'ɛ':[F[0]]}
  for final in aut2.F:
    tempF[final] = {'ɛ':[F[0]]}
  delta = {
    aut1.init[0][:-2]+aut2.init[0][:-2]+'q0' : {'ɛ': aut1.init+aut2.init},
    aut1.init[0][:-2]+aut2.init[0][:-2]+'qf' : {}
  }
  delta.update(aut1.delta)
  delta.update(aut2.delta)
  delta.update(tempF)

  M = automaton(sigma, Q, delta, init, F)
  return M

def concatAutomaton(aut1, aut2):
  sigma = list(set(aut1.sigma + aut2.sigma + ['ɛ']))
  init = [aut1.init[0]]
  F = aut2.F
  Q = list(set(aut1.Q + aut2.Q + init + F))
  delta = {}
  delta.update(aut1.delta)
  delta.update(aut2.delta)
  delta.update(
    dict(zip(aut1.F, [{'ɛ': aut2.init}]*len(aut1.F)))
  )
  # aut1F = ["E", "F"]
  # testInit = [{'ɛ':["aut2.init"]}]*len(aut1F)
  # teste = dict(zip(aut1F, testInit))
  M = automaton(sigma, Q, delta, init, F)
  return M

def starAutomaton(aut1):
  sigma = aut1.sigma + ['ɛ']
  tag = ''
  for var in aut1.sigma:
    tag += var
  init = [tag+"*q0"]
  F = [tag+"*qf"]
  Q = list(set(aut1.Q + init + F))
  delta = {
    tag+"*q0":{'ɛ':aut1.init+F}
  }
  delta.update(aut1.delta)
  delta.update(
    dict(zip(aut1.F, [{'ɛ': aut1.init+F}]*len(aut1.F)))
  )
  delta.update(
    {tag+"*qf":{}}
  )
  M = automaton(sigma, Q, delta, init, F)
  return M
  

# pagina 50
def erToAFNe(er):
  ops = ['.', '+']
  symbols = ['(', ')', ' ', ',']
  subStrings = []
  index = 0
  pairs = {}
  parent=[]

  for char in er:
    if char in ops:
      parent.append(index)
    if char == ')':
      pairs[parent.pop()] = index+1
    index = index + 1

  for key in pairs.keys():
    subStrings.append(er[key: pairs[key]])
  
  temp = subStrings[0]
  #if countParent(temp)==1:



  print(subStrings)


class automaton:
  def __init__(self, sigma, Q, delta, init, F):
    self.sigma = sigma
    self.Q = Q
    self.delta = delta
    self.init = init
    self.F = F

  def computeAux(self, input, actState, isInputConsume, newStates):
    if len(actState) != 0:    
      for state in actState:
        try:
          if 'ɛ' in self.delta[state].keys():
            if isInputConsume ==1: 
              newStates.update(self.delta[state]['ɛ'])
              #self.computeAux(input, self.delta[state]['ɛ'], 1, newStates)
              self.computeAux(input, [item for item in self.delta[state][input] if item not in actState], 1, newStates)
            else:
              self.computeAux(input, self.delta[state]['ɛ'], 0, newStates)

          if isInputConsume == 0:
            if input in self.delta[state].keys():
              #newStates.update(self.delta[state][input])
              self.computeAux(input, self.delta[state][input], 1, newStates)
          if isInputConsume == 1:
            newStates.update(actState) # [item for item in self.delta[state][input] if item not in actState]
            #self.computeAux(input, self.delta[state][input]-actState, 1, newStates)
            self.computeAux(input, [item for item in self.delta[state][input] if item not in actState], 1, newStates)
        except KeyError:
          return

  def compute(self, word):
    actual_state = set(self.init)
    for input in word:
      newStates=set()
      self.computeAux(input, actual_state, 0, newStates)
      print("("+str(actual_state)+", "+input+") -> "+str(newStates))
      actual_state = newStates

    for state in actual_state:
      if state in self.F:
        return True
    return False

  def render(self, fname):
    g = Digraph(format='png')
    g.node("qi", shape="point")
    for s in self.delta.keys():
        if self.init[0] in s:
            g.edge("qi", str(set(s)))
        for f in self.F:
            if f in s:
                g.node(str(set(s)), shape="doublecircle")
        for sym in self.sigma:
            g.edge(str(set(s)), str(set(self.delta[s][sym])), label=str(sym))
    g.render(fname)

  def printDelta(self):
    for item in self.delta:
      print("| "+item+" | "+str(self.delta[item])+" |")
  
  def is_total(self):
    for key in self.delta.keys():
        if len(self.delta[key]) != len(self.sigma):
            return False
    return True

  def getSigma(self):
    return self.sigma

  def getQ(self):
    return self.Q
  
  def getDelta(self):
    return self.delta

  def getInit(self):
    return self.init

  def getF(self):
    return self.F
  

# sigma =  ['0','1','ɛ']
# Q = ["A", "B", "C", "D", "E", 'F']
# init = ["A"] 
# F = ["E"] 
# delta = {
#     "A" : {'ɛ':['D'],'0' : ["B"], '1' : ["A"]},  
#     "B" : {'0' : ["C"], '1' : ["B"]},
#     "C" : {'0' : ["C"], '1' : ["C"]},
#     "D" : {'0' : ["E"], '1' : ["F"]},
#     "E" : {'0' : ["E"], '1' : ["E"]},
#     "F" : {"0" : ["F"], '1' : ["F"]}
# }

# M = automaton(sigma, Q, delta, init, F)
# print(M.compute('11'))
#M.render('aut1')


# sigma =  ['0','1']
# Q = ["A", "B", "C", "D"]
# init = ["A"] 
# F = ["C"] 
# delta = {
#     "A" : {'0' : ["B", "D"], '1' : ["C"]},  
#     "B" : {'0' : ["C"], '1' : ["D"]},
#     "C" : {'0' : ["C"], '1' : ["A"]},
#     "D" : {'0' : ["D"], '1' : ["D"]}
# }

# M = automaton(sigma, Q, delta, init, F)
# print(M.compute('001'))






A = generateBaseAutomaton("a")
# A.printDelta()
# print("sigma: "+str(A.getSigma()))
# print("Q: "+str(A.getQ()))
# print("F: "+str(A.getF()))
# print("init: "+str(A.getInit()))
#print(A.compute("aa"))

B = generateBaseAutomaton("b")
# print("delta: "+str(B.getDelta()))
# print("sigma: "+str(B.getSigma()))
# print("Q: "+str(B.getQ()))
# print("F: "+str(B.getF()))
# print("init: "+str(B.getInit()))
#print(B.compute("ab"))

X = generateBaseAutomaton("x")
Y = generateBaseAutomaton("y")

I = concatAutomaton(X, Y)

G = concatAutomaton(A, B)
# print("sigma: "+str(G.getSigma()))
# print("Q: "+str(G.getQ()))
# print("F: "+str(G.getF()))
# print("init: "+str(G.getInit()))
# G.printDelta()
print(G.compute('ab'))

Z = concatAutomaton(G, I)
print(Z.compute('abxy'))

T = starAutomaton(Z)
print(T.compute("abxyabbyabxy"))


H = starAutomaton(G)
#H.printDelta()
print(H.compute('ababababababababab'))


C = sumAutomaton(A,B)
# print("delta: "+str(C.getDelta()))
# print("sigma: "+str(C.getSigma()))
# print("Q: "+str(C.getQ()))
# print("F: "+str(C.getF()))
# print("init: "+str(C.getInit()))
print(C.compute("a"))

D = generateBaseAutomaton("d")
# print("delta: "+str(B.getDelta()))
# print("sigma: "+str(B.getSigma()))
# print("Q: "+str(B.getQ()))
# print("F: "+str(B.getF()))
# print("init: "+str(B.getInit()))
#print(D.compute("d"))

E = sumAutomaton(C, D)
#E.printDelta()
# print("sigma: "+str(E.getSigma()))
# print("Q: "+str(E.getQ()))
# print("F: "+str(E.getF()))
# print("init: "+str(E.getInit()))
print(E.compute('c'))




# print(M.is_total())
# M.render('autM')
#er = '+(.(+(a, d), b), +(c, d))'

#erToAFNe(er)

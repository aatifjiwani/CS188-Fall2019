# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        allStates = self.mdp.getStates()
        for _ in range(self.iterations):
            newValues = util.Counter()
            for state in allStates:
                if (self.mdp.isTerminal(state)):
                    newValues[state] = 0
                else:
                   possibleActions = self.mdp.getPossibleActions(state)
                   maxQVal = max([self.getQValue(state, action) for action in possibleActions])
                   newValues[state] = maxQVal
            
            self.values = newValues



    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        QValue = 0
        possibleStates = self.mdp.getTransitionStatesAndProbs(state, action)
        for possibleState in possibleStates:
            nextState, prob = possibleState
            reward = self.mdp.getReward(state, action, nextState)

            QValue = QValue + prob*(reward + self.discount*self.getValue(nextState))

        return QValue


    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if (self.mdp.isTerminal(state)):
            return None

        possibleActions = self.mdp.getPossibleActions(state)
        actionsToQvals = [(action, self.getQValue(state, action)) for action in possibleActions]
        maxAction = max(actionsToQvals, key = lambda x: x[1])

        return maxAction[0]

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()
        for i in range(self.iterations):
            state = states[i % len(states)]
            if (self.mdp.isTerminal(state)):
                    self.values[state] = 0
            else:
                possibleActions = self.mdp.getPossibleActions(state)
                maxQVal = max([self.getQValue(state, action) for action in possibleActions])
                self.values[state] = maxQVal


class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        self.predecessors = {}
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        self.computePred()
        pq = util.PriorityQueue()
        for state in self.mdp.getStates():
            if (not self.mdp.isTerminal(state)):
                curr = self.values[state]
                possibleActions = self.mdp.getPossibleActions(state)
                maxQVal = max([self.getQValue(state, action) for action in possibleActions])

                diff = abs(curr - maxQVal)

                pq.push(state, -diff)

        for iteration in range(self.iterations):
            if (pq.isEmpty()):
                break
            else:
                minState = pq.pop()
                if (not self.mdp.isTerminal(minState)):
                    possibleActions = self.mdp.getPossibleActions(minState)
                    maxQVal = max([self.getQValue(minState, action) for action in possibleActions])
                    self.values[minState] = maxQVal

                    for p in self.predecessors.get(minState, set()):
                        curr = self.values[p]
                        possibleActions = self.mdp.getPossibleActions(p)
                        maxQVal = max([self.getQValue(p, action) for action in possibleActions])

                        diff = abs(curr - maxQVal)

                        if (diff > self.theta):
                            pq.update(p, -diff)


    
    def computePred(self):
        states = self.mdp.getStates()
        for state in states:
            possibleActions = self.mdp.getPossibleActions(state)
            for action in possibleActions:
                possibleTransitions = self.mdp.getTransitionStatesAndProbs(state, action)
                for newState, prob in possibleTransitions:
                    if (prob > 0):
                        curr = self.predecessors.get(newState, set())
                        curr.add(state)
                        self.predecessors[newState] = curr


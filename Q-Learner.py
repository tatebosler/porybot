#TODO: How to deal with unknown values in Q-learner? --> Treat as probability
#TODO: Know attack slots for pokemon in play --> how to 
#Will have pokedex.getTypeEffectiveness function returns 2 if first type strong against second, return 1 if normal against second, 1/2 if weak against second, 0 if second is immune
#will also have pokedex.proportionAttack([your pokemon types], species)
import AIfinallogreader
import pokedex
class QLearningAgent:
	"""
	Q-Learning agent will try try to assign weights to our features



	Features:
		- type_atk1: 1 or 0. Whether p1 pokemon in play has an attack of strong type against opponent
		- bad_type_atk1: 1 or 0. Whether p1 pokemon in play has only weak attacks against p2
		- type_atk2: Whether p2 pokemon has attack strong against current p1 pokemon
		- bad_type_atk2 : same as before
		- hp1: HP of p1 pokemon in play
		- hp2: HP of p2 pokemon in play
		- hpsum1: Sum of hp of p1 pokemon not in play
		- hpsum2: Sum of hp of known p2 pokemon not in play

		- burn1: Whether p1 pokemon is burnt. permanent 
		- frz1: Whether p1 pokemon is frozen. permanent
		- par1 : whether p1 pokemon is paralyzed
		- psn1: whether p1 pokemon is poisoned
		- slp1 : whether p1 pokemon is asleep 
		- burn2: Whether p2 pokemon is burnt. permanent 
		- frz2: Whether p2 pokemon is frozen. permanent
		- par2 : whether p2 pokemon is paralyzed
		- psn2: whether p2 pokemon is poisoned
		- slp2 : whether p2 pokemon is asleep

		for your pokemon in play
		TODO: Add pokemon moves:

		- p1_moves: dictionary key is pokemon, values is list of tuples [move name, type, powr, stat_effects]

	"""

	def __init__(self):
		#TODO: INIT FUNCTIONS HERE
		# V-vals held in dict. Key is [list of weights]
		self.Vvals = {}


#getTypeofMove turned into getMove --> dictionary of info. has power and type
	def extract_atk1(self, game_state):
		p2 = game_state.getp2_in_play()
		p1 = game_state.getp1_in_play()
		p2_index = game_state.getp2_pokemon_names().index(p2)
		p1_index = game_state.getp1_pokemon_names().index(p1)
		p2_type = game_state.get_pokemon_types()[p2_index]
		type_atk1 = 0
		type_atk2 = 0
		# Find most effective move rating
		for attack in game_state.getp1_pokemon_moves()[p1]:
			attack_type = pokedex.getMove(attack)["type"]
			if pokedex.getTypeEffectiveness(attack_type, p2_type) > type_atk1 and pokedex.getMove(attack)["power"] > 0:
				type_atk1 = pokedex.getTypeEffectiveness(attack_type, p2_type)
		#Change to 1 or 0 feature values
		if type_atk1 == 2:
			self.type_atk1 = 1
			self.bad_type_atk1 = 0
		if type_atk1 == 1:
			self.type_atk1 = 0
			self.bad_type_atk1 = 0
		if type_atk1 < 1:
			self.type_atk1 = 0
			self.bad_type_atk1 = 1


	def extract_atk2(self, game_state):
		p1 = game_state.getp1_in_play()
		p2 = game_state.getp2_in_play()
		p2_index = game_state.getp2_pokemon_names().index(p2)
		p1_index = game_state.getp1_pokemon_names().index(p1)
		p1_type = game_state.get_pokemon_types()[p1_index]
		type_atk2 = 0
		for attack in game_state.getp2_pokemon_moves()[p2]:
			attack_type = pokedex.getMove(attack)["type"]
			if pokedex.getTypeEffectiveness(attack_type, p1_type) > type_atk2 and pokedex.getMove(attack)["power"] > 0:
				type_atk1 = pokedex.getTypeEffectiveness(attack_type, p1_type)
		if type_atk2 == 2:
			self.type_atk2 = 1
			self.bad_type_atk2 = 0
		if type_atk2 == 1:
			self.type_atk2 = 0
			self.bad_type_atk2 = 0
		if type_atk2 < 1:
			self.type_atk2 = 0
			self.bad_type_atk2 = 1

	def extract_hps(self,game_state):
		p1 = game_state.getp1_in_play()
		p2 = game_state.getp2_in_play()
		p2_index = game_state.getp2_pokemon_names().index(p2)
		p1_index = game_state.getp1_pokemon_names().index(p1)
		self.hp1 = game_state.getp1_hp()[p1_index]
		self.hp2 = game_state.getp2_hp()[p2_index]
		self.hpsum1 = 0
		for i in game_state.getp1_hp():
			self.hpsum1 += int(i)
		for i in game_state.getp2_hp():
			self.hpsum2 += int(i)

	def updateFeatures(self,game_state):
		self.extract_hps()
		self.extract_atk1()
		self.extract_atk2()

	def extractFeatures(self):
		"""
		Returns [type_atk1, bad_type_atk1, type_atk2, bad_type_atk2, hp1, hp2, hpsum1, hpsum2]
		"""
		return [self.type_atk1, self.bad_type_atk1, self.type_atk2, self.bad_type_atk2, self.hp1, self.hp2, self.hpsum1, self.hpsum2]

	def getQValue(self, game_state, action):
		#TODO: impliment
		for move in game_state.getp1_pokemon_moves()



	def updateWeights(self, features, nextState):
		vVal = float('inf')*-1
		#TODO: how to get legal actions in a state? --> will not be a constant function
        for act in self.getLegalActions(state):
            q = self.getQValue(state, act)
            if q > vVal:
                vVal = q
        self.Vvals[str(nextState)] = vVal
        qVal = self.Qvals[self., action]
        for feature in features:
            weight = self.weights[feature]
            difference = self.Vvals[nextState] * self.discount + reward - qVal
            self.weights[feature] = self.weights[feature] + self.alpha*difference*features[feature]



	def getAction(self, features):

	def runTrainingData(self):
		logs = AIfinallogreader.main()
		for log in logs:
			#Run through each game, learn weights
			for state in log.getLog():
				






'''
		for i in game_state.getp2_in_play:
			#Will have pokedex.getTypeEffectiveness function returns 2 if first type strong against second, return 1 if normal against second, 1/2 if weak against second, 0 if second is immune
			#will also have pokedex.proportionAttack([your pokemon types], species)
			
			#if p2 playing pokemon has attack strong against p1 pokemon, type_atk2 = true
			if 
'''










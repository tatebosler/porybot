#TODO: How to deal with unknown values in Q-learner? --> Treat as probability
#TODO: Know attack slots for pokemon in play --> how to 
#TODO: HOW DO EXPRESS ACTION IN STATE SPACE??
#Will have pokedex.getTypeEffectiveness function returns 2 if first type strong against second, return 1 if normal against second, 1/2 if weak against second, 0 if second is immune
#will also have pokedex.proportionAttack([your pokemon types], species)
import AIfinallogreader
import pokedex
class QLearningAgent:
	"""
	Q-Learning agent will try try to assign weights to our features

	reward must be (hp2 - hp1)??

	reward for winning should be super high --> 1000000?



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
		-p1_move_power
		-p1_move_type_effectiveness


		- p1_moves: dictionary key is pokemon, values is list of tuples [move name, type, powr, stat_effects]

	"""
	"""
	Features:
		- type_atk1: 1 or 0. Whether p1 uses attack strong against opponent
		- bad_type_atk1: 1 or 0. Whether p1 uses attack weak against opponent
		- type_atk2: Whether p2 uses attack strong against you
		- bad_type_atk2 : Whether p2 uses attack weak against you
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
		#weights in order [type_atk1, bad_type_atk1,type_atk2,bad_type_atk2,hp1,hp2,hpsum1,hpsum2]
		self.weights = [0,0,0,0,0,0,0,0]


#getTypeofMove turned into getMove --> dictionary of info. has power and type
	def extract_atk(self, game_state):
		move1 = pokedex.getMove(game_state.getp1_action())
		move2 = pokedex.getMove(game_state.getp2_action())
		p2 = game_state.getp2_in_play()
		p1 = game_state.getp1_in_play()
		p2_index = game_state.getp2_pokemon_names().index(p2)
		p1_index = game_state.getp1_pokemon_names().index(p1)
		p1_type = game_state.getp1_pokemon_types()[p1_index]
		p2_type = game_state.getp2_pokemon_types()[p2_index]
		type_atk1 = pokedex.getTypeEffectiveness(move1[type],p2_type)
		type_atk2 = pokedex.getTypeEffectiveness(move2[type],p1_type)
		#Change to 1 or 0 feature values
		if type_atk1 == 2:
			type_atk1 = 1
			bad_type_atk1 = 0
		if type_atk1 == 1:
			type_atk1 = 0
			bad_type_atk1 = 0
		if type_atk1 < 1:
			type_atk1 = 0
			bad_type_atk1 = 1
		if type_atk2 == 2:
			type_atk2 = 1
			bad_type_atk2 = 0
		if type_atk2 == 1:
			type_atk2 = 0
			bad_type_atk2 = 0
		if type_atk2 < 1:
			type_atk2 = 0
			bad_type_atk2 = 1
		return [type_atk1,bad_type_atk1, type_atk2, bad_type_atk2]
#Commented code will be good for Q-learning in real time, not from transcripts
'''
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
			type_atk1 = 1
			bad_type_atk1 = 0
		if type_atk1 == 1:
			type_atk1 = 0
			bad_type_atk1 = 0
		if type_atk1 < 1:
			type_atk1 = 0
			bad_type_atk1 = 1
		return [type_atk1,bad_type_atk1]


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
'''

	def extract_hps(self,game_state):
		p1 = game_state.getp1_in_play()
		p2 = game_state.getp2_in_play()
		p2_index = game_state.getp2_pokemon_names().index(p2)
		p1_index = game_state.getp1_pokemon_names().index(p1)
		hp1 = game_state.getp1_hp()[p1_index]
		hp2 = game_state.getp2_hp()[p2_index]
		hpsum1 = 0
		hpsum2 = 0
		for i in game_state.getp1_hp():
			self.hpsum1 += int(i)
		for i in game_state.getp2_hp():
			self.hpsum2 += int(i)
		return [hp1, hp2, hpsum1, hpsum2]


	def extractFeatures(self, game_state):
		"""
		Returns [type_atk1, bad_type_atk1, type_atk2, bad_type_atk2, hp1, hp2, hpsum1, hpsum2]
		"""
		return [self.extract_atk(game_state)[0], self.extract_atk(game_state)[1],self.extract_atk(game_state)[2], self.extract_atk2(game_state)[3], self.extract_hps(game_state)[0], self.extract_hps(game_state)[1], self.extract_hps(game_state)[2], self.extract_hps(game_state)[3]]

	def getQValue(self, feature_vector, action, next_feature_vector):
		#TODO: impliment
		Q_value = 0
		for i in range(len(next_feature_vector)):
			feature = feature_vector[i]
			weight = self.weights[i]
			Q_value += feature*weight
		return Q_value


	def getLegalActions(self,state):
		return state.getp1_pokemon_moves()[state.getp1_in_play()]

	def updateWeightsTraining(self, features, action):
        for act in self.getLegalActions(features):
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
				#update the feature values for the state we're looking at
				self.updateFeatures(state)
				#








'''
		for i in game_state.getp2_in_play:
			#Will have pokedex.getTypeEffectiveness function returns 2 if first type strong against second, return 1 if normal against second, 1/2 if weak against second, 0 if second is immune
			#will also have pokedex.proportionAttack([your pokemon types], species)
			
			#if p2 playing pokemon has attack strong against p1 pokemon, type_atk2 = true
			if 
'''










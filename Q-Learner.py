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
		self.weights = [0,0,0,0]
		self.gamma = 1
		self.rounds = 0
		self.apha = 0


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

	def extract_hps(self,game_state):
		p1 = game_state.getp1_in_play()
		p2 = game_state.getp2_in_play()
		p2_index = game_state.getp2_pokemon_names().index(p2)
		p1_index = game_state.getp1_pokemon_names().index(p1)
		hp1 = game_state.getp1_hp()[p1_index]
		hp2 = game_state.getp2_hp()[p2_index]
		return [hp2-hp1]

	def extractFeatures(self, game_state):
		"""
		Returns [type_atk1, bad_type_atk1, type_atk2, bad_type_atk2, hp1, hp2, hpsum1, hpsum2]
		"""
		return [self.extract_atk(game_state)[0], self.extract_atk(game_state)[1],self.extract_atk(game_state)[2], self.extract_atk(game_state)[3]]

	def extractReward(self,game_state):
		return game_state.get_p2_hp_change - game_state.get_p1_hp_change


	def getQValue(self, state):
		#TODO: impliment f
		Q_value = 0
		feature_vector = self.extractFeatures(state)
		for i in range(len(feature_vector)):
			feature = feature_vector[i]
			weight = self.weights[i]
			Q_value += feature*weight
		return Q_value


	def getLegalActions(self,state):
		return state.getp1_pokemon_moves()[state.getp1_in_play()]

	def updateWeightsTraining(self, game_state, next_game_state):
		Q_val = self.getQValue(game_state)
        Q_val_next = self.getQValue(next_game_state)
        r = self.extractReward(game_state)
        difference = (r+self.gamma * Q_val_next) - Q_val
        features = self.extractFeatures(game_state)
        for i in range(len(self.weights)):
        	self.weights[i] = self.weights[i]+difference*features[i]

	def runTrainingData(self):
		logs = AIfinallogreader.main()
		for log in logs:
			#Run through each game, learn weights
			self.rounds += 1
			self.alpha = 1/self.rounds
			for i in len(log.getLog()):
				#update the feature values for the state we're looking at
				game_state = log.getLog[i]
				next_state = log.getLog[i+1]
				self.updateWeightsTraining(game_state, )
				self.updateFeatures(state)
				#
			print self.weights


def main():
	Qlearner = QLearningAgent()
	Qlearner.runTrainingData()

main()








'''
		for i in game_state.getp2_in_play:
			#Will have pokedex.getTypeEffectiveness function returns 2 if first type strong against second, return 1 if normal against second, 1/2 if weak against second, 0 if second is immune
			#will also have pokedex.proportionAttack([your pokemon types], species)
			
			#if p2 playing pokemon has attack strong against p1 pokemon, type_atk2 = true
			if 
'''










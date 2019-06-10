#Will have Pokedex.getTypeEffectiveness function returns 2 if first type strong against second, return 1 if normal against second, 1/2 if weak against second, 0 if second is immune
#will also have Pokedex.proportionAttack([your pokemon types], species)

#TODO: deal with edge case of reading last state in a game
#TODO: Add features: remaining unfainted pokemon p1, unfainted pkm p2, add win or loss reward of 3,000
import AIfinallogreader
from pokedex import Pokedex
import math

class QLearningAgent:
	"""
	Q-Learning agent will try try to assign weights to our features



	Features:
		- type_atk1: 1 or 0. Whether p1 pokemon in play has an attack of strong type against opponent
		- norm_type_atk1: 1 or 0. Whether p1 pokemon in play has a normal strength attack against opponent
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
		#weights in order [type_atk1*power_atk1*STAB1, type_atk2*power_atk2*STAB2, p1_unfainted, p2_unfainted, par1, slp1, tox1, frz1, brn1, par2, slp2, tox2, frz2, brn2]
	weights = []
	gamma = 1
	seen = 0
	alpha = 0

	def __init__(self):
		#TODO: INIT FUNCTIONS HERE
		# V-vals held in dict. Key is [list of weights]
		self.Vvals = {}
		#weights in order [type_atk1, bad_type_atk1,type_atk2,bad_type_atk2,hp1,hp2,hpsum1,hpsum2]
		self.weights = []
		for i in range(14): #change back to 14
			self.weights.append(0)
		self.gamma = 1
		self.seen = 0
		self.alpha = 1

	#TODO: Change attack effectiveness to just be 1 var for each pokemon
	#TODO: 
	def extract_atk(self, game_state):
		'''
		Returns booleans for all attack type effectiveness features
		'''
		p2 = game_state.getp2_in_play()
		p1 = game_state.getp1_in_play()
		p2_index = game_state.getp2_pokemon_names().index(p2)
		p1_index = game_state.getp1_pokemon_names().index(p1)
		p1_type = game_state.getp1_pokemon_types()[p1_index]
		p2_type = game_state.getp2_pokemon_types()[p2_index]
		STAB1 = 1
		STAB2 = 1
		type_atk1 = 0
		power_atk1 = 0
		type_atk2 = 0
		power_atk2 = 0
		if game_state.getp1_action() != "switch" and game_state.getp1_action() != "None":
			move1 = Pokedex.getMove(game_state.getp1_action())
			if move1['type'] in p1_type:
				STAB1 = 1.5
		else:
			move1 = None
		if game_state.getp2_action() != "switch" and game_state.getp2_action() != "None":
			move2 = Pokedex.getMove(game_state.getp2_action())
			if move2['type'] in p2_type:
				STAB2 = 1.5
		else:
			move2 = None
		#TODO: REMOVE TYPE EFFECTIVENESS ON STATUS MOVES
		if move1 != None:
			type_atk1 = Pokedex.getTypeEffectiveness(move1['type'],p2_type)
			power_atk1 = move1['power']
			if power_atk1 == None:
				power_atk1 = 0
		if move2 != None:
			type_atk2 = Pokedex.getTypeEffectiveness(move2['type'],p1_type)
			power_atk2 = move2['power']
			if power_atk2 == None:
				power_atk2 = 0
		return [type_atk1*power_atk1*STAB1, type_atk2*power_atk2*STAB2]

	def extract_atk_effects(self, game_state):
		#TODO: IMPLIMENT THIS AND GET TATE TO DO BACK END
		return

	def extract_effects(self, game_state):
		#TODO: Fix for multiple simultaneous effects
		p1 = game_state.getp1_in_play()
		p2 = game_state.getp2_in_play()
		p2_index = game_state.getp2_pokemon_names().index(p2)
		p1_index = game_state.getp1_pokemon_names().index(p1)
		p1_effects = game_state.get_p1_stats()
		p2_effects = game_state.get_p2_stats()
		p1_effect = p1_effects[p1_index]
		p2_effect = p2_effects[p2_index]
		#par1, slp1, tox1, frz1, brn1,
		p1_par = 0
		p1_slp = 0
		p1_tox = 0
		p1_frz = 0
		p1_brn = 0
		for i in p1_effects:
			if i == "par":
				p1_par += 1
			if i == "slp":
				p1_slp += 1
			if i == "tox":
				p1_tox += 1
			if i == "frz":
				p1_frz += 1
			if i == "brn":
				p1_brn += 1
		"""
		if p1_effect == "par":
			p1_par = 1
		if p1_effect == "slp":
			p1_slp = 1
		if p1_effect == "tox":
			p1_tox = 1
		if p1_effect == "frz":
			p1_frz = 1
		if p1_effect == "brn":
			p1_brn = 1
			"""
		p2_par = 0
		p2_slp = 0
		p2_tox = 0
		p2_frz = 0
		p2_brn = 0
		for i in p2_effects:
			if i == "par":
				p2_par += 1
			if i == "slp":
				p2_slp += 1
			if i == "tox":
				p2_tox += 1
			if i == "frz":
				p2_frz += 1
			if i == "brn":
				p2_brn += 1
		"""
		if p2_effect == "par":
			p2_par = 1
		if p2_effect == "slp":
			p2_slp = 1
		if p2_effect == "tox":
			p2_tox = 1
		if p2_effect == "frz":
			p2_frz = 1
		if p2_effect == "brn":
			p2_brn = 1
		"""

		return [p1_par, p1_slp, p1_tox, p1_frz, p1_brn, p2_par, p2_slp, p2_tox, p2_frz, p2_brn]

	def extract_hps(self,game_state):
		p1 = game_state.getp1_in_play()
		p2 = game_state.getp2_in_play()
		p2_index = game_state.getp2_pokemon_names().index(p2)
		p1_index = game_state.getp1_pokemon_names().index(p1)
		hp1 = game_state.getp1_hp()[p1_index]
		hp2 = game_state.getp2_hp()[p2_index]
		return [hp2-hp1]

	def extract_remaining_pokemon(self, game_state):
		p1_hps = game_state.getp1_hp()
		remaining1 = 0
		for i in p1_hps:
			if int(i) > 0:
				remaining1 += 1
		p2_hps = game_state.getp2_hp()
		remaining2 = 0
		for i in p2_hps:
			if int(i) > 0:
				remaining2 += 1
		return [remaining1, remaining2]

	def extractFeatures(self, game_state):
		"""
		Returns [type_atk1, norm_type_atk1, bad_type_atk1, type_atk2, norm_type_atk2, bad_type_atk2, remaining1, remaining2, p1_par, p1_slp, p1_tox, p1_frz, p1_brn, p2_par, p2_slp, p2_tox, p2_frz, p2_brn]
		"""
		atk = self.extract_atk(game_state)
		remaining = self.extract_remaining_pokemon(game_state)
		stats = self.extract_effects(game_state)
		to_return = []
		#for group in [atk,remaining,stats]:
		for group in [remaining,stats]:
			for i in range(len(group)):
				to_return.append(group[i])
		to_return.append(game_state.get_p1_heal())
		to_return.append(game_state.get_p2_heal())
		return to_return

	def extractReward(self,game_state):
		sum_max1 = 0
		for i in game_state.get_p1_max_hps():
			sum_max1 += int(i)
		sum_max2 = 0
		for i in game_state.get_p2_max_hps():
			sum_max2 += int(i)
		reward = (game_state.get_p2_hp_change()/sum_max2) - (game_state.get_p1_hp_change()/sum_max1)
		return reward

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
		self.seen += 1
		self.alpha = 1/(self.seen**(1.0/10.0))
		if next_game_state == None:
			#deal with last state edge case here
			Q_val = self.getQValue(game_state)
			hpsum1 = 0
			for i in game_state.getp1_hp():
				hpsum1 += int(i)
			if hpsum1 > 0:
				r = 3000
				difference = r - Q_val
				features = self.extractFeatures(game_state)
				for i in range(len(self.weights)):
					self.weights[i] = self.weights[i]+self.alpha*difference*features[i]
			else:
				r = -3000
				difference = r - Q_val
				features = self.extractFeatures(game_state)
				for i in range(len(self.weights)):
					self.weights[i] = self.weights[i]+self.alpha*difference*features[i]
		else:
			Q_val = self.getQValue(game_state)
			Q_val_next = self.getQValue(next_game_state)
			r = self.extractReward(game_state)
			difference = (r+self.gamma * Q_val_next) - Q_val
			features = self.extractFeatures(game_state)
			for i in range(len(self.weights)):
				self.weights[i] = self.weights[i]+self.alpha*difference*features[i]
	def runTrainingData(self):
		logs = AIfinallogreader.test()
		for log in logs:
			#Run through each game, learn weights
			for i in range(len(log.getLog())):
				#update the feature values for the state we're looking at
				#edge case for last state
				if i == len(log.getLog())-1:
					game_state = log.getLog()[i]
					self.updateWeightsTraining(game_state, None)
				else:
					game_state = log.getLog()[i]
					next_state = log.getLog()[i+1]
					self.updateWeightsTraining(game_state, next_state)
			feature_labels = ["unfainted 1:   ", "unfainted 2:   ", "par1:  ", "slp1:  ", "tox1:  ", "frz1:  ", "brn1:  ", "par2:  ", "slp2:  ", "tox2:  ", "frz2:  ", "brn2:  ", "heal 1: ", "heal 2:  "]
			for i in range(len(self.weights)):
				print feature_labels[i], self.weights[i]
			print("alpha:  ", self.alpha)







	#Below this point is learning and acting in real life games:
	#Impliment ALL OF THESE
	def getGameState(self, OTHER_INPUTS_HERE):
		"""
		Needs to interact with plugin and return 
		"""
		#TODO: IMPLIMENT
		return


	def calculateDamage(self, move_name, user_pokemon, reciever_pokemon, reciever_hp):
		'''
		Does not include probability of hitting
		'''
		move = Pokedex.getMove[move_name]
		user_type = Pokedex.get(user_pokemon)['type']
		reciever_type = Pokedex.get(reciever_pokemon)['type']
		STAB = 1
		if move['type'] in user_type:
			STAB = 1.5
		type_multiplier = Pokedex.getTypeEffectiveness(move['type'], reciever_type)
		damage = STAB * type_multiplier * move['power']
		return damage



	def calculateExpectedNextState(self, move_name, current_game_state):
		#true_effect = anticipated reward, anticipated
		#TODO: FINISH IMPLIMENTATION --> expected damage from attack, expected change in status features, expected effect on own hp. 
		#TODO: FIGURE OUT ORDER OF TURNS
		move = Pokedex.getMove[move_name]
		effect_id = move['effect_id']
		effect_prob = Pokedex.effects['effect_prob']
		effect = Pokedex.effects[effect_id]
		p1 = current_game_state.getp1_in_play()
		p2 = current_game_state.getp2_in_play()
		p1_index = current_game_state.getp1_pokemon_names.index(p1)
		p2_index = current_game_state.getp2_pokemon_names.index(p2)
		p1_hp = current_game_state.getp1_hp()
		p2_hp = current_game_state.getp2_hp()
		damage = self.calculateDamage(move_name, p1, p2, p2_hp)
		if effect == "heal":
			max_hp = current_game_state.get_p1_max_hps()[p1_index]
			if move == "rest":
				if .5*max_hp+current_game_state.getp1_hp()[p1_index] < max_hp:
					p1_expected_hp = .5*max_hp+current_game_state.getp1_hp()[p1_index] * effect_prob + current_game_state.getp1_hp()[p1_index]*(1-effect_prob)
				else:
					p1_expected_hp = max_hp*effect_prob
			elif move == "rest":
				p1_expected_hp = max_hp * effect_prob
			else:
				p1_expected_hp = .5*damage + p1_hp
		if effect == "opponent_status:psn":
			#IMPLIMENT HERE TO SHOW THAT THEY GET POISONED
			pass







	def getLegalActionsRealTime(self, game_State):
		"""
		Give back list of legal actions in the form [[list of move names], [list of unfainted pokemon]]
		"""
		#TODO: IMPLIMENT
		return

	def getFeatureValuesRealTime(self, game_State, action):
		p2 = game_State.getp2_in_play()
		p2_all = game_State.getp2_pokemon_names()
		#Type effectiveness for current pokemon --> if opponent 
		if game_State.getp2_hp(p2_all.index):
			pass
		#calculate probability that current opponent has move strong against you --> this x 


	def getQValueRealTime(self, game_state):
		#TODO: impliment
		return


def main():
	Qlearner = QLearningAgent()
	Qlearner.runTrainingData()

main()



# if 




'''
		for i in game_state.getp2_in_play:
			#Will have Pokedex.getTypeEffectiveness function returns 2 if first type strong against second, return 1 if normal against second, 1/2 if weak against second, 0 if second is immune
			#will also have Pokedex.proportionAttack([your pokemon types], species)
			
			#if p2 playing pokemon has attack strong against p1 pokemon, type_atk2 = true
			if 
'''

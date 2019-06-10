#Will have Pokedex.getTypeEffectiveness function returns 2 if first type strong against second, return 1 if normal against second, 1/2 if weak against second, 0 if second is immune
#will also have Pokedex.proportionAttack([your pokemon types], species)

#TODO: deal with edge case of reading last state in a game
#TODO: Add features: remaining unfainted pokemon p1, unfainted pkm p2, add win or loss reward of 3,000
import AIfinallogreader
from pokedex import Pokedex
import math
from numpy.random import choice
import numpy.random

class QLearningAgent:
	"""
	Q-Learning agent will try try to assign weights to our features



	Features:
		- type_atk1: 0 to 4. type effectiveness multiplier 
		- type_atk2: 0 to 4. type effectiveness multiplier 
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


		TODO: Add pokemon moves:

		- p1_moves: dictionary key is pokemon, values is list of tuples [move name, type, powr, stat_effects]

	"""
		#weights in order [type_atk1*power_atk1*STAB1, type_atk2*power_atk2*STAB2, p1_unfainted, p2_unfainted, par1, slp1, tox1, frz1, brn1, par2, slp2, tox2, frz2, brn2]
	weights = []
	gamma = 1.0
	seen = 0
	alpha = 0

	def __init__(self):
		#TODO: INIT FUNCTIONS HERE
		#weights in order [type_atk1, bad_type_atk1,type_atk2,bad_type_atk2,hp1,hp2,hpsum1,hpsum2]
		self.weights = []
		for i in range(12): #change back to 14
			self.weights.append(0)
		self.gamma = 1.0
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
		elif game_state.getp1_action() == "None":
			if p1 in game_state.getp1_pokemon_moves().keys():
				moves = game_state.getp1_pokemon_moves()[p1]
				move1 = moves[numpy.random.choice(range(len(moves)))]
				move1 = Pokedex.getMove(move1)
			else:
				moves = Pokedex.getLegalMoves(p1)
				move1 = moves[numpy.random.choice(range(len(moves)))]['name']
				move1 = Pokedex.getMove(move1)
		else:
			move1 = None
		if game_state.getp2_action() != "switch" and game_state.getp2_action() != "None":
			move2 = Pokedex.getMove(game_state.getp2_action())
			if move2['type'] in p2_type:
				STAB2 = 1.5
		elif game_state.getp2_action() == "None":
			if p2 in game_state.getp2_pokemon_moves().keys():
				moves = game_state.getp2_pokemon_moves()[p2]
				move2 = moves[numpy.random.choice(range(len(moves)))]
				move2 = Pokedex.getMove(move2)
			else:
				moves = Pokedex.getLegalMoves(p2)
				move2 = moves[numpy.random.choice(range(len(moves)))]['name']
				move2 = Pokedex.getMove(move2)
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
		'''
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
		'''
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
		p2_par = 0
		p2_slp = 0
		p2_tox = 0
		p2_frz = 0
		p2_brn = 0
		'''
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
		'''
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

		#return [p1_par, p1_slp, p1_tox, p1_frz, p1_brn, p2_par, p2_slp, p2_tox, p2_frz, p2_brn]
		return [p1_par, p1_tox, p1_brn, p2_par, p2_tox, p2_brn]

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
		for group in [atk,remaining,stats]:
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
		reward = 100*(float(game_state.get_p2_hp_change())/sum_max2) - 100*(float(game_state.get_p1_hp_change())/sum_max1)
		print(reward)
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
		self.alpha = .00001
		#self.alpha = .0000000000001/(self.seen**(1.0/10.0))
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
		logs = AIfinallogreader.main()
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
			#feature_labels = ['atk1: ', "atk2:  ", "unfainted 1:   ", "unfainted 2:   ", "par1:  ", "slp1:  ", "tox1:  ", "frz1:  ", "brn1:  ", "par2:  ", "slp2:  ", "tox2:  ", "frz2:  ", "brn2:  ", "heal 1: ", "heal 2:  "]
			feature_labels = ['atk1: ', "atk2:  ", "unfainted 1:   ", "unfainted 2:   ", "par1:  ", "tox1:  ", "brn1:  ", "par2:  ", "tox2:  ", "brn2:  ", "heal 1: ", "heal 2:  "]
			for i in range(len(self.weights)):
				print feature_labels[i], self.weights[i]
			print("alpha:  ", self.alpha)
	def returnWeights(self):
		return self.weights





class QlearningAgentOnline:


	#Below this point is learning and acting in real life games:
	#Impliment ALL OF THESE
	#TODO: MAKE NEW CLASS TO HOLD REAL TIME INFO
	"""
	Random player :
	if opponent type strong against your type, switch
	maximize immediate reward --> hp1_change-hp2_change

	"""
	def __init__(self, weights):
		#TODO: INIT FUNCTIONS HERE
		#weights in order [type_atk1, bad_type_atk1,type_atk2,bad_type_atk2,hp1,hp2,hpsum1,hpsum2]
		self.weights = weights

	def calculateDamage(self, move_name, user_pokemon, reciever_pokemon, reciever_hp):
		#accuracy removed
		move = Pokedex.getMove(move_name)
		user_type = Pokedex.get(user_pokemon)['type']
		reciever_type = Pokedex.get(reciever_pokemon)['type']
		STAB = 1
		if move['type'] in user_type:
			STAB = 1.5
		type_multiplier = Pokedex.getTypeEffectiveness(move['type'], reciever_type)
		power = 0 if move['power'] is None else move['power']
		damage = STAB * type_multiplier * power
		return damage


	def getFirstPlayer(self, my_team, active_index, opponent_pokemon, move_name):
		#SHould return "[1,2]" if p1 expected to go first, "[2,1]" otherwise
		#For now, assume p1 goes first
		my_speed = my_team[active_index]['speed']
		opponent_speed = Pokedex.getAverageSpeed(opponent_pokemon['name'])
		if my_team[active_index]['status'] == 'PAR':
			my_speed /= 4
		if opponent_pokemon['status'] == 'PAR':
			opponent_speed /= 4
		if my_speed > opponent_speed:
			return [1, 2]
		elif my_speed < opponent_speed:
			return [2, 1]
		else:
			return random.shuffle([1, 2])

	def calculateExpectedNextFeatures(self,active_index, current_features, move_name, my_team, opponent_pokemon):
		#true_effect = anticipated reward, anticipated
		#TODO: FINISH IMPLIMENTATION --> expected damage from attack, expected change in status features, expected effect on own hp. 
		#TODO: FIGURE OUT ORDER OF TURNS
		next_state_features = current_features
		if move_name == 'None':
			move_name = 'Growl'
		move = Pokedex.getMove(move_name)
		effect_id = move['effect_id']
		effect_prob = move['effect_prob']
		if effect_id in Pokedex.effects.keys():
			effect = Pokedex.effects[effect_id]
		else:
			effect = 'None'
		p1 = my_team[active_index]
		p2 = opponent_pokemon
		p1_faint = 0
		p2_faint = 0
		order = self.getFirstPlayer(my_team,active_index,opponent_pokemon,move_name)
		atk1 = self.calculateDamage(move_name, p1['name'], p2['name'], p1['current_hp'])*move['accuracy']
		if 'par' in p1['status']:
			atk1 = atk1 *.75
		next_state_features['atk1'] = damage2
		if self.calculateDamage(move_name, p1['name'], p2['name'], p2['current_hp']) > p2['current_hp']:
			#doesn't include possibility of opponent switch
			next_state_features['remaining2']=current_features['remaining1']-move['accuracy']
			p2_faint = move['accuracy']
		if effect == "heal":
			max_hp = p1['hp']
			if move == "rest":
				if .5*max_hp+p1['current_hp'] < max_hp:
					heal1 = .5*max_hp+p1['current_hp']* effect_prob
				else:
					heal1 = max_hp*effect_prob - p1['current_hp']
			elif move == "rest":
				heal1 = max_hp*effect_prob - p1['current_hp']
			else:
				heal1 = .5*atk1
			next_state_features['heal1']=heal1
		if effect == "opponent_status:psn":
			if current_features['tox2'] < 1:
				next_state_features['tox2']= move['effect_prob']
		elif effect == "opponent_status:par":
			if current_features['par2'] < 1:
				next_state_features['par2']= move['effect_prob']
		elif effect == "opponent_status:brn":
			if current_features['brn2'] < 1:
				next_state_features['brn2']= move['effect_prob']
		atk2 = 0
		avg_accuracy = 0
		for i in opponent_pokemon['known_moves']:
			atk2 += Pokedex.getMove(i)*self.calculateDamage(i,my_team[active_index]['name'],opponent_pokemon['name'],opponent_pokemon['current_hp'])/4
			avg_accuracy += Pokedex.getMove(i)['accuracy']/4
		for num in 4-current_game_state.getp2_pokemon_moves().keys():
			poss_moves2 = Pokedex.getLegalMoves(opponent_pokemon['name'])
			move_added = False
			while not move_added:
				i = numpy.random(range(len(poss_moves2)))
				if i not in opponent_pokemon['known_moves']:
					atk2 += Pokedex.getMove(i)*self.calculateDamage(i,my_team[active_index]['name'],opponent_pokemon['name'],opponent_pokemon['current_hp'])/4
					avg_accuracy += Pokedex.getMove(i)['accuracy']/4
					move_added = True
		next_state_features['atk2'] = atk2*avg_accuracy
		if order[0] == 1:
			next_state_features['atk2'] = atk2*(1-move['accuracy'])
		if atk2 > p1_hp:
			next_state_features['remaining1']=current_features['remaining1']-avg_accuracy
			p1_faint = avg_accuracy
		if order[0] == 2:
			next_state_features['atk1'] = next_state_features['atk1']*(1-avg_accuracy)
		#Not dealing with effects on p1, too difficult to account for
		next_state_features['par1'] = current_features['par1']
		next_state_features['tox1'] = current_features['tox1']
		next_state_features['brn1'] = current_features['brn1']
		print(next_state_features)
		return next_state_features
		

# if switch, dictionary 'name':switch_to + pokemon name, 'index':index, 

	def getFeatureValuesRealTime(self, my_team, active_index, opponent_team, opponent_active_index):
		#feature_labels = ['atk1: ', "atk2:  ", "unfainted 1:   ", "unfainted 2:   ", "par1:  ", "tox1:  ", "brn1:  ", "par2:  ", "tox2:  ", "brn2:  ", "heal 1: ", "heal 2:  "]
		features = {}
		for i in ["par1", "tox1", "brn1"]:
			if my_team[active_index]['status'] in i:
				features[i]=1
			else:
				features[i]=0
		for i in ["par2", "tox2", "brn2"]:
			if opponent_team[opponent_active_index]['status'] in i:
				features[i]=1
			else:
				features[i]=0
		features['heal1'] = 0
		features['heal2'] = 0
		features['atk1'] = 0
		features['atk2'] = 0
		return features




		#calculate probability that current opponent has move strong against you --> this x 

	def updateWeightsRealTime(self, features, reward, next_possible_actions, next_features):
		alpha = .00001
		#self.alpha = .0000000000001/(self.seen**(1.0/10.0))
		#deal with last state edge case here
		Q = 0
		for i in range(len(self.weights)):
			Q += self.weights[i]*features[labels[i]] 

		'''
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
	'''

	def returnQValues(self,possible_actions, my_team, active_index, opponent_team, opponent_active_index):
		'''
		Uses softmax to choose action
		'''
		current_features = self.getFeatureValuesRealTime(my_team, active_index, opponent_team, opponent_active_index)
		labels = ['atk1', "atk2", "unfainted 1", "unfainted 2", "par1", "tox1", "brn1", "par2", "tox2", "brn2", "heal1", "heal2"]
		best_feature = None
		Qvals = []
		for action in possible_actions:
			if action['name'] == 'switch_to':
				features = current_features
				#CONTINUE HERE, CHANGE STATUS FEATURES FOR P1
				p1 = my_team[action['index']]
				features['par1']=0
				features['tox1']=0
				features['brn1']=0
				if p1['status'] == 'par':
					features['par1']=1
				if p1['status'] == 'tox':
					features['tox1']=1
				if p1['status'] == 'brn':
					features['brn1']=1
			else:
				Q = 0
				features = self.calculateExpectedNextFeatures(active_index, current_features, action['name'], my_team, opponent_team[opponent_active_index])
			for i in range(len(self.weights)):
				Q += self.weights[i]*features[labels[i]]
			Qvals.append(Q)
		return Qvals

	def chooseAction(self,possible_actions, Qvalues):
		for i in range(len(Qvalues)):
			Qvalues[i]= math.exp(Qvalues[i])
		Qsum = numpy.sum(Qvalues)
		for i in range(len(Qvalues)):
			Qvalues[i]= Qvalues[i]/Qsum
		return choice(possible_actions,1,Qvalues)







# if 




'''
		for i in game_state.getp2_in_play:
			#Will have Pokedex.getTypeEffectiveness function returns 2 if first type strong against second, return 1 if normal against second, 1/2 if weak against second, 0 if second is immune
			#will also have Pokedex.proportionAttack([your pokemon types], species)
			
			#if p2 playing pokemon has attack strong against p1 pokemon, type_atk2 = true
			if 
'''

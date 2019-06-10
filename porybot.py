# This Python file uses the following encoding: utf-8
# The file used to control the game via the command line.

from pokedex import Pokedex
import QLearner
import random
import numpy
import math
import sys

my_team = Pokedex.randomTeam()
opponent_team = Pokedex.randomTeam()
second_player_can_move = True
interactive = False
active_index = -1
opponent_active_index = -1
separator = ', '
Q_agent = None

def main():
	global interactive
	global Q_agent
	global my_team
	global opponent_team
	
	print "Importing log data and weights..."
	print "This might take a moment. Thanks for your patience."
	Q_learning_agent = QLearner.QLearningAgent()
	Q_learning_agent.runTrainingData()
	weights = Q_learning_agent.returnWeights()
	Q_agent = QLearner.QlearningAgentOnline(weights)
	print "All finished!"
	
	p1wins = 0
	p2wins = 0
	games = 1
	for arg in sys.argv:
		if "--num-games=" in arg:
			gameSplit = arg.split("=")
			games = int(gameSplit[1])
	
	if "--interactive" in sys.argv:
		interactive = True
	
	for i in range(games):
		for pokemon in my_team:
			pokemon['current_hp'] = pokemon['hp']
			pokemon['known_moves'] = []
			pokemon['seen'] = False
			pokemon['status'] = 'None'
		for pokemon in opponent_team:
			pokemon['current_hp'] = pokemon['hp']
			pokemon['known_moves'] = []
			pokemon['seen'] = False
			pokemon['status'] = 'None'
		if interactive:
			print "A random team has been generated for you. Please choose your first Pokémon:"
		switchIn()
		opponentRandomSwitch()
		while True:
			my_choice = startTurn()
			opponent_choice = makeOpponentChoice()
			action_order = calculateSpeed(my_choice, opponent_choice)
			will_act_self = calculateAndSampleAction(my_choice, my_team[active_index]['status'])
			will_act_opponent = calculateAndSampleAction(opponent_choice, opponent_team[opponent_active_index]['status'])
			
			second_player_can_move = True
			act(action_order, will_act_self, my_choice, will_act_opponent, opponent_choice)
			
			your_team_hp = [pokemon['current_hp'] for pokemon in my_team]
			opponent_team_hp = [pokemon['current_hp'] for pokemon in opponent_team]
			
			print ""
			if numpy.sum(your_team_hp) <= 0 or numpy.sum(opponent_team_hp) <= 0:
				if numpy.sum(your_team_hp) <= 0:
					print "PLAYER 2 WINS"
					p2wins += 1
				if numpy.sum(opponent_team_hp) <= 0:
					print "PLAYER 1 WINS"
					p1wins += 1
				break
	
	print "Player 1 wins: {}/{}".format(p1wins, games)
		
def act(action_order, will_act_self, my_choice, will_act_opponent, opponent_choice):
	global second_player_can_move
	
	if action_order is None:
		action_order = random.shuffle([1, 2])
	
	if action_order[0] == 1:
		act_self(will_act_self, my_choice)
		if second_player_can_move:
			act_opponent(will_act_opponent, opponent_choice)
	else:
		act_opponent(will_act_opponent, opponent_choice)
		if second_player_can_move:
			act_self(will_act_self, my_choice)

def act_self(will_act_self, my_choice):
	global opponent_active_index
	global active_index
	
	if will_act_self:
		if "Switch to" in my_choice['name']:
			switchIn(my_choice['index'])
		else:
			print "You used", my_choice['name']
			if my_choice['power'] > 0:
				move_damage = damage(my_choice['power'], my_choice['type'], opponent_team[opponent_active_index]['type'], my_team[active_index]['type'], my_team[active_index]['attack'], opponent_team[opponent_active_index]['defense'])
				print "Damage:", move_damage
				opponent_team[opponent_active_index]['current_hp'] -= move_damage
				print "New opponent HP: {}/{}".format(opponent_team[opponent_active_index]['current_hp'], opponent_team[opponent_active_index]['hp'])
				if opponent_team[opponent_active_index]['current_hp'] <= 0:
					opponent_team[opponent_active_index]['current_hp'] = 0
					second_player_can_move = False
					opponent_active_index = -1
					opponentRandomSwitch()
			else:
				print "It's a status move! No damage dealt."
	else:
		print "You tried to act, but couldn't (either because your attack missed or a status is in effect that prevents action)."

def act_opponent(will_act_opponent, opponent_choice):
	global opponent_active_index
	global active_index
	
	if will_act_opponent:
		if "Switch to" in opponent_choice['name']:
			switchIn(opponent_choice['index'])
		else:
			print "Your opponent used", opponent_choice['name']
			if opponent_choice['power'] > 0:
				move_damage = damage(opponent_choice['power'], opponent_choice['type'], opponent_team[opponent_active_index]['type'], opponent_team[opponent_active_index]['type'], opponent_team[opponent_active_index]['defense'], my_team[active_index]['defense'])
				print "Damage:", move_damage
				my_team[active_index]['current_hp'] -= move_damage
				print "Your new HP: {}/{}".format(my_team[active_index]['current_hp'], my_team[active_index]['hp'])
				if my_team[active_index]['current_hp'] <= 0:
					my_team[active_index]['current_hp'] = 0
					second_player_can_move = False
					active_index = -1
					switchIn()
			else:
				print "It's a status move! No damage dealt."
	else:
		print "Your opponent tried to act, but couldn't (either because their attack missed or a status is in effect that prevents action)."

def damage(power, moveType, defType, atkType, attack, defense):
	stab = 1.5 if moveType in atkType else 1.0
	effectiveness = Pokedex.getTypeEffectiveness(moveType, defType)
	if effectiveness > 1:
		print "It's super effective!"
	ratio = float(attack) / float(defense)
	
	return math.floor(((42 * power * ratio) / 50.0 + 2) * stab * effectiveness)

def calculateAndSampleAction(action, status):
	actionModifier = 0.75 if status in ["PAR", "CONFUSED"] else 1.0
	power = 0 if ("power" not in action.keys() or action['power'] is None) else action['power']
	if "Switch to" in action['name']:
		return True
	elif status in ["FRZ", "SLP"]:
		return False
	elif power == 0 and action['effect_id'] in Pokedex.effects.keys():
		effects = Pokedex.effects[action['effect_id']]
		effProb = 0 if action['effect_prob'] is None else action['effect_prob']
		if "stat_self_increase" in effects or "heal" in effects:
			return sampleActionWithProbability(1.0 * actionModifier)
		else:
			return sampleActionWithProbability(effProb * actionModifier)
	else:
		return sampleActionWithProbability(action['accuracy'] * actionModifier)

def sampleActionWithProbability(prob):
	return random.random() <= prob

def calculateSpeed(my_choice, opponent_choice):
	my_speed = my_team[active_index]['speed']
	opponent_speed = opponent_team[opponent_active_index]['speed']
	if my_team[active_index]['status'] == 'PAR':
		my_speed /= 4
	if opponent_team[opponent_active_index]['status'] == 'PAR':
		opponent_speed /= 4
	
	if "Switch to" in my_choice:
		return [1, 2]
	elif "Switch to" in opponent_choice:
		return [2, 1]
	elif my_speed > opponent_speed:
		return [1, 2]
	elif my_speed < opponent_speed:
		return [2, 1]
	else:
		return random.shuffle([1, 2])

def makeOpponentChoice():
	global Q_agent
	global my_team
	global active_index
	global opponent_team
	global opponent_active_index
	
	if "--random" in sys.argv:
		return random.choice(opponent_team[opponent_active_index]['moves'])
	else:
		active_pokemon = opponent_team[opponent_active_index]
		actions = active_pokemon['moves'][:]
		for i, pokemon in enumerate(opponent_team):
			if pokemon['current_hp'] > 0 and i != opponent_active_index:
				actions.append({'name': 'Switch to '+pokemon['name'], 'index': i})
		
		Qvals = Q_agent.returnQValues(actions, opponent_team, opponent_active_index, my_team, active_index)
		action = Q_agent.chooseAction(actions, Qvals)
		if isinstance(action, numpy.ndarray):
			action = list(action)[0]
		return action

def startTurn():
	global Q_agent
	global my_team
	global active_index
	global opponent_team
	global opponent_active_index
	
	active_pokemon = my_team[active_index]
	print "What will {} do?".format(active_pokemon['name'])
	actions = active_pokemon['moves'][:]
	for i, pokemon in enumerate(my_team):
		if pokemon['current_hp'] > 0 and i != active_index:
			actions.append({'name': 'Switch to '+pokemon['name'], 'index': i})
	if interactive:
		return actions[makeSelection([action['name'] for action in actions])]
	else:
		Qvals = Q_agent.returnQValues(actions, my_team, active_index, opponent_team, opponent_active_index)
		action = Q_agent.chooseAction(actions, Qvals)
		if isinstance(action, numpy.ndarray):
			action = list(action)[0]
		return action

def opponentRandomSwitch():
	global opponent_active_index

	if opponent_active_index is not -1:
		print "Your opponent withdrew {}.".format(opponent_team[opponent_active_index]['name'])
	
	legalSwitch = False
	myTeamHP = [pokemon['current_hp'] for pokemon in opponent_team]
	if numpy.sum(myTeamHP) <= 0:
		opponent_active_index = -1
		return
	while not legalSwitch:
		opponent_active_index = random.randint(0, 5)
		legalSwitch = opponent_team[opponent_active_index]['current_hp'] > 0
		
	their_pokemon = opponent_team[opponent_active_index]
	print "Your opponent sent out {}. HP remaining: {}/{}".format(their_pokemon['name'], their_pokemon['current_hp'], their_pokemon['hp'])

def switchIn(index = None):
	global active_index
	
	if interactive:
		if index is None:
			index = makeSelection(["{} (type: {}; moves: {})".format(pokemon['name'], separator.join(list(pokemon['type'])), separator.join([move['name'] for move in pokemon['moves']])) for pokemon in my_team], [i for i in range(len(my_team)) if my_team[i]['current_hp'] <= 0])
		if active_index is not -1:
			print "You withdrew {}.".format(my_team[active_index]['name'])
		active_index = index
		my_pokemon = my_team[active_index]
		print "You sent out {}. HP remaining: {}/{}".format(my_pokemon['name'], my_pokemon['current_hp'], my_pokemon['hp'])
	else:
		if index is None:
			legalSwitch = False
			myTeamHP = [pokemon['current_hp'] for pokemon in my_team]
			if numpy.sum(myTeamHP) <= 0:
				active_index = -1
				return
			while not legalSwitch:
				index = random.randint(0, 5)
				legalSwitch = my_team[index]['current_hp'] > 0
		if active_index is not -1:
			print "You withdrew {}.".format(my_team[active_index]['name'])
		active_index = index
		my_pokemon = my_team[active_index]
		print "You sent out {}. HP remaining: {}/{}".format(my_pokemon['name'], my_pokemon['current_hp'], my_pokemon['hp'])

def makeSelection(actions, excludeKeys = []):
	for i, action in enumerate(actions):
		if i not in excludeKeys:
			print "[{}] {}".format(i + 1, action)
	input = raw_input(">>> ")
	return int(input) - 1

main()

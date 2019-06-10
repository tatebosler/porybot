# This Python file uses the following encoding: utf-8
# The file used to control the game via the command line.

from pokedex import Pokedex
import QLearner
import random
import sys

my_team = Pokedex.randomTeam()
opponent_team = Pokedex.randomTeam()
continue_battle = True
active_index = -1
opponent_active_index = -1
separator = ', '

def main():
	for pokemon in my_team:
		pokemon['current_hp'] = pokemon['hp']
		pokemon['status'] = None
	for pokemon in opponent_team:
		pokemon['current_hp'] = pokemon['hp']
		pokemon['known_moves'] = []
		pokemon['seen'] = False
		pokemon['status'] = None
	print "A random team has been generated for you. Please choose your first Pokémon:"
	switchIn()
	opponentRandomSwitch()
	while continue_battle:
		my_choice = startTurn()
		opponent_choice = makeOpponentChoice()
		action_order = calculateSpeed(my_choice, opponent_choice)
		will_act_self = calculateAndSampleAction(my_choice, my_team[active_index]['status'])
		will_act_opponent = calculateAndSampleAction(opponent_choice, opponent_team[opponent_active_index]['status'])
		break

def calculateAndSampleAction(choice, status):
	actionModifier = 0.75 if status in ["PAR", "CONFUSED"] else 1.0
	if "Switch to" in action:
		return True
	elif status in ["FRZ", "SLP"]:
		return False
	elif action['power'] == 0 and action['effect_id'] in Pokedex.effects.keys():
		effects = Pokedex.effects[action['effect_id']]
		if "stat_self_increase" in effects or "heal" in effects:
			return sampleActionWithProbability(1.0 * actionModifier)
		else:
			return sampleActionWithProbability(action['effect_prob'] * actionModifier)
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
		return [1, 2]
	else:
		return random.shuffle([1, 2])

def makeOpponentChoice():
	# For now - randomly chooses an attack move, even if it's inefficient.
	return random.choice(opponent_team[opponent_active_index]['moves'])

def startTurn():
	active_pokemon = my_team[active_index]
	print "What will {} do?".format(active_pokemon['name'])
	actions = active_pokemon['moves'][:]
	for i, pokemon in enumerate(my_team):
		if pokemon['current_hp'] > 0 and i != active_index:
			actions.append({'name': 'Switch to '+pokemon['name'], 'index': i})
	return actions[makeSelection([action['name'] for action in actions])]

def opponentRandomSwitch():
	global opponent_active_index

	if opponent_active_index is not -1:
		print "Your opponent withdrew {}.".format(opponent_team[opponent_active_index]['name'])
	active_index = random.randint(0, 5)
	their_pokemon = opponent_team[opponent_active_index]
	print "Your opponent sent out {}. HP remaining: {}/{}".format(their_pokemon['name'], their_pokemon['current_hp'], their_pokemon['hp'])

def switchIn():
	global active_index
	
	index = makeSelection(["{} (type: {}; moves: {})".format(pokemon['name'], separator.join(list(pokemon['type'])), separator.join([move['name'] for move in pokemon['moves']])) for pokemon in my_team])
	if active_index is not -1:
		print "You withdrew {}.".format(my_team[active_index]['name'])
	active_index = index
	my_pokemon = my_team[active_index]
	print "You sent out {}. HP remaining: {}/{}".format(my_pokemon['name'], my_pokemon['current_hp'], my_pokemon['hp'])

def makeSelection(actions):
	for i, action in enumerate(actions):
		print "[{}] {}".format(i + 1, action)
	input = raw_input(">>> ")
	return int(input) - 1

main()

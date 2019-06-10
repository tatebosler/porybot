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
	for pokemon in opponent_team:
		pokemon['current_hp'] = pokemon['hp']
		pokemon['known_moves'] = []
	print "A random team has been generated for you. Please choose your first Pokémon:"
	switchIn()
	opponentRandomSwitch()
	while continue_battle:
		startTurn()
		break

def startTurn():
	active_pokemon = my_team[active_index]
	print "What will {} do?".format(active_pokemon['name'])
	actions = active_pokemon['moves'][:]
	for i, pokemon in enumerate(my_team):
		if pokemon['current_hp'] > 0 and i != active_index:
			actions.append({'name': 'Switch to '+pokemon['name'], 'index': i})
	choice = makeSelection([action['name'] for action in actions])

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
	active_index = index - 1
	my_pokemon = my_team[active_index]
	print "You sent out {}. HP remaining: {}/{}".format(my_pokemon['name'], my_pokemon['current_hp'], my_pokemon['hp'])

def makeSelection(actions):
	for i, action in enumerate(actions):
		print "[{}] {}".format(i + 1, action)
	input = raw_input(">>> ")
	return int(input)

main()

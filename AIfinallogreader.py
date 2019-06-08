#TODO: Get tate to play a game, figure out how to know what we know originally
#TODO: Add way to remember types
from pokedex import Pokedex

class GameLog:
	"""A class to hold the info of one game. Should be a series of gamestate objects"""
	#List of game states. One state for each of player 1's turns
	game_states = []

	def __init__(self):
		"""
		Inputs: list of p1 pokemon names
		In the first round of the game when reading, we will know names 
		of all p1 pokemon but not necessarily hp. Will fill in p1_pokemon dictinary
		with what we have, but will have to likely back propogate info as we read through the doc
		"""
		self.game_states = []

	def add_start_state(self,p1_pokemon_names,p2_pokemon_names):
		p1_pokemon_names = {}
		p2_pokemon = {}
		for name in p1_pokemon_names:
			p1_pokemon_names[name] = 0
		for name in p2_pokemon_names:
			p1_pokemon_names[name] = 0
		start_state = gamestate(p1_pokemon,p2_pokemon)
		self.game_states.append(start_state)

	def add_state(self,state):
		self.game_states.append(state)

	def update_past_hp(self,pokemon_name, pokemon_hp):
		for state in self.game_states:
			state.update_player_1(pokemon_name, pokemon_hp, [])

	def update_past_moves(self,player,pokemon_name, move):
		for state in self.game_states:
			state.update_moves(player, pokemon_name, move)

	def update_past_pokemon(self, player, pokemon_name):
		#TODO: Impliment, backpropogate knowlege about pokemon
		return True

	def getLog(self):
		return self.game_states

	def printSelf(self):
		for state in self.game_states:
			state.printSelf()

#TODO: types not mentioned in log. need a resource to check against
#TODO: should hold attacks each pokemon has --> add dictionary of attacks used for each pokemon
class GameState:
	"""
	A class to hold the features of a turn in a game
	"""
	#Dictionary with pokemon names as keys, [type,hp,status_effects] as values
	# names as keys because multiple pokemon of same type on one team would be confusing

	p2_pokemon_names = []
	p2_pokemon_hp = []
	p2_pokemon_status = []
	p2_pokemon_moves = {}
	p2_pokemon_types = []
	p2_action = None
	#hold index of pokemon currently in play
	p2_in_play = None

	p1_pokemon_names = []
	p1_pokemon_hp = []
	p1_pokemon_status = []
	p1_pokemon_moves = {}
	p1_action = None
	p1_pokemon_types = []
	#hold index of pokemon currently in play
	p1_in_play = None

	def __init__(self, p2_pokemon_names, p2_pokemon_hp, p2_pokemon_status,
	p2_action, p2_in_play, p1_pokemon_names, p1_pokemon_hp, p1_pokemon_status,
	p1_action, p1_in_play):
		"""
		Constructor for one gamestate --> state/action pair
		"""	
		self.p2_pokemon_names = p2_pokemon_names
		self.p2_pokemon_hp = p2_pokemon_hp
		self.p2_pokemon_status = p2_pokemon_status
		self.p2_action = p2_action
		self.p2_in_play = p2_in_play
		self.p2_pokemon_moves = {}
		self.p2_pokemon_types = []

		for pokemon in p2_pokemon_names:
			self.p2_pokemon_types.append(Pokedex.get(pokemon)["type"])

		self.p1_pokemon_names = p1_pokemon_names
		self.p1_pokemon_hp = p1_pokemon_hp
		self.p1_pokemon_status = p1_pokemon_status
		self.p1_action = p1_action
		self.p1_in_play = p1_in_play
		self.p1_pokemon_moves = {}
		self.p1_pokemon_types = []

		for pokemon in p1_pokemon_names:
			self.p1_pokemon_types.append(Pokedex.get(pokemon)["type"])

	def update_player_1(self,pokemon_name,pokemon_hp,pokemn_status_effects):
		"""
		To be used to backpropogate information
		"""
		#TODO: UPDATE TYPES HERE TOO
		self.p1_pokemon_names.append(pokemon_name)
		self.p1_pokemon_hp.append(pokemon_hp)
		self.p1_pokemon_status.append(pokemn_status_effects) 
	
	def update_moves(self,player, pokemon, move):
		if player == "1":
			if pokemon not in self.p1_pokemon_moves.keys():
				self.p1_pokemon_moves[pokemon] = [move]
			oldMoves = self.p1_pokemon_moves[pokemon]
			if move not in oldMoves:
				oldMoves.append(move)
				self.p1_pokemon_moves[pokemon] = oldMoves
		else:
			if pokemon not in self.p2_pokemon_moves.keys():
				self.p2_pokemon_moves[pokemon] = [move]
			oldMoves = self.p2_pokemon_moves[pokemon]
			if move not in oldMoves:
				oldMoves.append(move)
				self.p2_pokemon_moves[pokemon] = oldMoves

	def getp2_in_play(self):
		return self.p2_in_play

	def getp1_in_play(self):
		return self.p1_in_play

	def getp2_pokemon_names(self):
		return self.p2_pokemon_names

	def getp1_pokemon_names(self):
		return self.p1_pokemon_names

	def getp2_pokemon_types(self):
		return self.p2_pokemon_types

	def getp1_pokemon_types(self):
		return self.p1_pokemon_types

	def getp1_pokemon_moves(self):
		return self.p1_pokemon_moves

	def getp2_pokemon_moves(self):
		return self.p2_pokemon_moves

	def getp1_hp(self):
		return self.p1_pokemon_hp

	def getp2_hp(self):
		return self.p2_pokemon_hp

	def printSelf(self):
		print(self.p2_pokemon_names)
		print(self.p2_pokemon_hp)
		print(self.p2_pokemon_status)
		print(self.p2_action)
		print(self.p2_in_play)
		print(self.p2_pokemon_moves)
		print(self.p2_pokemon_types)




	#TODO: make get functions


def readLog(text_file):
	log = text_file.readlines()
	p2_pokemon_names = [] 
	p2_pokemon_hp = []
	p2_pokemon_status = []
	p2_action = None
	p2_in_play = None
	p1_pokemon_names = [] 
	p1_pokemon_hp = [] 
	p1_pokemon_status = []
	p1_action = None
	p1_in_play = None
	game_log = GameLog()

	for line in log:
		print(line[0:8])

		if line[0:8] in "|switch|":
			if line[9] == "1":
				#p1 switched in new pokemon
				p1_action = "switch"
				line = line[13:]
				line_split = line.split("|")
				p1_in_play = line_split[1]
				if p1_in_play not in p1_pokemon_names:
					p1_pokemon_names.append(p1_in_play)
					#no status effects when first introduced
					p1_pokemon_status.append("None")
					#add HP info
					hp = line.split("|")[-1]
					hp = hp.split("/")[0]
					#can just append bc we know pokemon is being added for the first time
					p1_pokemon_hp.append(hp)
					game_log.update_past_hp(p1_in_play,hp)
				print("switch 1: ", p1_in_play, p1_pokemon_names)

			elif line[9] == "2":
				#p2 switched in new pokemon
				p2_action = "switch"
				line = line[13:]
				line_split = line.split("|")
				p2_in_play = line_split[1]
				if p2_in_play not in p2_pokemon_names:
					p2_pokemon_names.append(p2_in_play)
					p2_pokemon_status.append("None")
					hp = line.split("|")[-1]
					hp = hp.split("/")[0]
					#can just append bc we know pokemon is being added for the first time
					p2_pokemon_hp.append(hp)
				print("switch 2: ", p2_in_play, p2_pokemon_names)
			else:
				#there was a weird switch I wasn't prepared for, throw an error
				print("SOMETHING HAS GONE WORNG: no player number attatched to switch statement")
				print("Line id",line[9])
		if "|-damage|" in line:
			#apply damage to hp values
			print("damage: ", line)
			if line[10] == "1":
				#reset p1 pokemon health
				new_health = line.split("|")
				new_health = new_health[3].split("/")[0]
				print("new health: ", new_health)
				p1_pokemon_hp[p1_pokemon_names.index(p1_in_play)] = new_health
			elif line[10] == "2":
				#reset p2 pokemon health
				new_health = line.split("|")
				new_health = new_health[3].split("/")[0]
				print("new health: ", new_health)
				print("Pokemon:  ", p2_in_play)
				p2_pokemon_hp[p2_pokemon_names.index(p2_in_play)] = new_health
			else:
				print("SOMETHING HAS GONE WORNG: no player number attatched to damage statement")
				print("Line id: ", line[9])
		if "|-heal|" in line:
			#apply damage to hp values
			if line[8] == "1":
				#reset p1 pokemon health
				new_health = line.split("|")
				new_health = new_health[3].split("/")[0]
				p1_pokemon_hp[p1_pokemon_names.index(p1_in_play)] = new_health
			elif line[8] == "2":
				#reset p2 pokemon health
				new_health = line.split("|")
				new_health = new_health[3].split("/")[0]
				p2_pokemon_hp[p2_pokemon_names.index(p2_in_play)] = new_health
			else:
				print("SOMETHING HAS GONE WORNG: no player number attatched to heal statement")
				print("line id: ", line[8])
		if "|cant|" in line:
			#apply damage to hp values
			if line[7] == "1":
				#reset p1 pokemon health
				p1_action = "None"
			elif line[7] == "2":
				#reset p2 pokemon health
				p2_action = "None"
			else:
				print("SOMETHING HAS GONE WORNG: no player number attatched to cant statement")
				print("Line id: ", line[7])
		if "|move|" in line:
			#apply damage to hp values
			if line[7] == "1":
				#save move
				move = line.split("|")[3]
				print("Move: ", move)
				p1_action = move
				game_log.update_past_moves("1",p1_in_play, move)
			elif line[7] == "2":
				#reset p2 pokemon health
				move = line.split("|")[3]
				p2_action = move
				print("Move: ", move)
				game_log.update_past_moves("2",p2_in_play, move)
			else:
				print("SOMETHING HAS GONE WORNG: no player number attatched to damage statement")
		if "|-status|" in line:
			#apply damage to hp values
			if line[11] == "1":
				#NOTE: THIS DOESN'T ALLOW MULTIPLE STATUSES --> FIX LATER
				stat = line.split("|")[3]
				p1_pokemon_status[p1_in_play] = stat
			elif line[11] == "2":
				#reset p2 pokemon health
				stat = line.split("|")[3]
				p2_pokemon_status[p2_in_play] = stat
			else:
				print("SOMETHING HAS GONE WORNG: no player number attatched to status statement")
		if "|turn|" in line:
			game_state = GameState(p2_pokemon_names, p2_pokemon_hp, p2_pokemon_status, p2_action, p2_in_play, p1_pokemon_names, p1_pokemon_hp, p1_pokemon_status, p1_action, p1_in_play)
			game_log.add_state(game_state)
	return game_log

def main():
	f = open("logs/920774993.txt")
	the_log = readLog(f)
	the_log.printSelf()



main()



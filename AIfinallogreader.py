#TODO: MAKE VARIABLE TO REMEMBER MAX HP OF POKEMON
from pokedex import Pokedex
import os

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
		# update HP changes
		if len(self.game_states) > 0:
			prev_hp1 = self.game_states[-1].getp1_hp()
			prev_hp1_sum = 0
			for i in prev_hp1:
				prev_hp1_sum += int(i)
			prev_hp2 = self.game_states[-1].getp2_hp()
			prev_hp2_sum = 0
			for i in prev_hp2:
				prev_hp2_sum += int(i)
			hp1 = state.getp1_hp()
			hp1_sum = 0
			for i in hp1:
				hp1_sum += int(i)
			hp2 = state.getp2_hp()
			hp2_sum = 0
			for i in hp2:
				hp2_sum += int(i)
			state.update_p1_hp_change(prev_hp1_sum - hp1_sum)
			state.update_p2_hp_change(prev_hp2_sum - hp2_sum)
		#add new state
		self.game_states.append(state)

	def update_past_hp(self,player,pokemon_name, pokemon_hp):
		for state in self.game_states:
			if player == "1":
				state.update_player_1(pokemon_name, pokemon_hp)
			else:
				state.update_player_2(pokemon_name, pokemon_hp)
	"""
	def update_past_moves(self,player,pokemon_name, move):
		for state in self.game_states:
			state.update_moves(player, pokemon_name, move)
	"""

	def getLog(self):
		return self.game_states

	def printSelf(self):
		turn = 0
		for state in self.game_states:
			print "______"
			print("Turn: ", turn)
			state.printSelf()
			turn += 1
			print "______"


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
	p1_action, p1_in_play, p1_moves, p2_moves):
		"""
		Constructor for one gamestate --> state/action pair
		"""	
		#the weird way I'm instantiating list variables is because they keep changing when the inputs change
		#want names and moves to be same throughout all states
		self.p2_pokemon_names = p2_pokemon_names
		self.p2_pokemon_hp = []
		for i in p2_pokemon_hp:
			self.p2_pokemon_hp.append(i)
		self.p2_pokemon_status = []
		for i in p2_pokemon_status:
			self.p2_pokemon_status.append(i)
		self.p2_action = p2_action
		self.p2_in_play = p2_in_play
		self.p2_pokemon_moves = p2_moves
		self.p2_pokemon_types = []
		for pokemon in p2_pokemon_names:
			self.p2_pokemon_types.append(Pokedex.get(pokemon)["type"])
		self.p2_hp_change = 0

		self.p1_pokemon_names = p1_pokemon_names
		self.p1_pokemon_hp = []
		for i in p1_pokemon_hp:
			self.p1_pokemon_hp.append(i)
		self.p1_pokemon_status = []
		for i in p1_pokemon_status:
			self.p1_pokemon_status.append(i)
		self.p1_action = p1_action
		self.p1_in_play = p1_in_play
		self.p1_pokemon_moves = p1_moves
		self.p1_pokemon_types = []

		self.p1_hp_change = 0


		for pokemon in p1_pokemon_names:
			self.p1_pokemon_types.append(Pokedex.get(pokemon)["type"])

	def update_player_1(self,pokemon_name,pokemon_hp):
		"""
		To be used to backpropogate information
		"""
		#Use this because p1_pokemon_names updates automatically
		if len(self.p1_pokemon_names) > len(self.p1_pokemon_hp):
			self.p1_pokemon_hp.append(pokemon_hp)
			self.p1_pokemon_status.append("None")
			self.p1_pokemon_types.append(Pokedex.get(pokemon_name)["type"])

	def update_player_2(self,pokemon_name,pokemon_hp):
		"""
		To be used to backpropogate information
		"""
		#Use this because p1_pokemon_names updates automatically
		if len(self.p2_pokemon_names) > len(self.p2_pokemon_hp):
			self.p2_pokemon_hp.append(pokemon_hp)
			self.p2_pokemon_status.append("None")
			self.p2_pokemon_types.append(Pokedex.get(pokemon_name)["type"])
	"""
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
	"""
	def getp1_action(self):
		return self.p1_action

	def getp2_action(self):
		return self.p2_action

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

	def update_p1_hp_change(self, p1_hp_change):
		self.p1_hp_change = p1_hp_change

	def update_p2_hp_change(self, p2_hp_change):
		self.p2_hp_change = p2_hp_change

	def get_p1_hp_change(self):
		return self.p1_hp_change

	def get_p2_hp_change(self):
		return self.p2_hp_change

	def get_p1_stats(self):
		return self.p1_pokemon_status

	def get_p2_stats(self):
		return self.p2_pokemon_status



	def printSelf(self):

		#print"P1 Names:  ", self.p1_pokemon_names
		#print"P2 Names:  ", self.p2_pokemon_names
		#print"P1 in play:  ", self.p1_in_play
		#print"P2 in play:  ", self.p2_in_play

		#print"P1 action:  ",self.p1_action
		#print"P2 action:  ",self.p2_action

		#print"P1 moves:  ", self.p1_pokemon_moves
		#print"P2 moves:  ", self.p2_pokemon_moves
		#print"P1 types:  ", self.p1_pokemon_types
		#print"P2 types:  ", self.p2_pokemon_types
		print"P1 hp:  ", self.p1_pokemon_hp
		print"P2 hp:   ", self.p2_pokemon_hp

		print"P1 hp change:  ", self.p1_hp_change
		print"P2 hp change:  ", self.p2_hp_change

		#print"P1 statuses:  ", self.p1_pokemon_status
		#print"P2 statuses:  ", self.p2_pokemon_status
		







	#TODO: make get functions


def readLog(text_file):
	log = text_file.readlines()
	p2_pokemon_names = [] 
	p2_pokemon_hp = []
	p2_pokemon_status = []
	p2_action = None
	p2_in_play = None
	p2_moves = {}
	p1_pokemon_names = [] 
	p1_pokemon_hp = [] 
	p1_pokemon_status = []
	p1_action = None
	p1_in_play = None
	p1_moves = {}
	game_log = GameLog()

	for line in log:
		if line[0:8] in "|switch|":
			if line[9] == "1":
				#p1 switched in new pokemon
				p1_action = "switch"
				line = line[13:]
				line_split = line.split("|")
				p1_in_play = line_split[1]
				p1_in_play = p1_in_play.split(",")[0]
				#add new pokemon to the lists only if it hasn't been played yet
				if p1_in_play not in p1_pokemon_names:
					#print("Pokemon  ", p1_in_play, " not in ", p1_pokemon_names)
					p1_pokemon_names.append(p1_in_play)
					#no status effects when first introduced
					p1_pokemon_status.append("None")
					#add HP info
					hp = line.split("|")[-1]
					hp = hp.split("/")[0]
					#can just append bc we know pokemon is being added for the first time
					p1_pokemon_hp.append(hp)
					game_log.update_past_hp("1",p1_in_play,hp)
				#print("switch 1: ", p1_in_play, p1_pokemon_names)

			elif line[9] == "2":
				#p2 switched in new pokemon
				p2_action = "switch"
				line = line[13:]
				line_split = line.split("|")
				p2_in_play = line_split[1]
				p2_in_play = p2_in_play.split(",")[0]
				if p2_in_play not in p2_pokemon_names:
					p2_pokemon_names.append(p2_in_play)
					p2_pokemon_status.append("None")
					hp = line.split("|")[-1]
					hp = hp.split("/")[0]
					#can just append bc we know pokemon is being added for the first time
					p2_pokemon_hp.append(hp)
					game_log.update_past_hp("2",p2_in_play,hp)
				#print("switch 2: ", p2_in_play, p2_pokemon_names)
			else:
				#there was a weird switch I wasn't prepared for, throw an error
				print("SOMETHING HAS GONE WORNG: no player number attatched to switch statement")
				print("Line id",line[9])
		if "|-damage|" in line:
			#apply damage to hp values
			if line[10] == "1":
				#reset p1 pokemon health
				new_health = line.split("|")
				new_health = new_health[3].split("/")[0]
				new_health = new_health.split(" ")[0]
				p1_pokemon_hp[p1_pokemon_names.index(p1_in_play)] = new_health
			elif line[10] == "2":
				#reset p2 pokemon health
				new_health = line.split("|")
				new_health = new_health[3].split("/")[0]
				new_health = new_health.split(" ")[0]
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
				p1_action = move
				if p1_in_play in p1_moves.keys():
					oldMoves = p1_moves[p1_in_play]
					if move not in oldMoves:
						oldMoves.append(move)
						p1_moves[p1_in_play] = oldMoves
				else:
					p1_moves[p1_in_play] = [move]
				#game_log.update_past_moves("1",p1_in_play, move)
			elif line[7] == "2":
				#reset p2 pokemon health
				move = line.split("|")[3]
				p2_action = move
				if p2_in_play in p2_moves.keys():
					oldMoves = p2_moves[p2_in_play]
					if move not in oldMoves:
						oldMoves.append(move)
						p2_moves[p2_in_play] = oldMoves
				else:
					p2_moves[p2_in_play] = [move]
			else:
				print("SOMETHING HAS GONE WORNG: no player number attatched to damage statement")
		if "|-status|" in line:
			#apply damage to hp values
			#TODO: maybe fix so that multiple statuses can exist at same time AND fix the fact that some statuses go away
			if line[10] == "1":
				#NOTE: THIS DOESN'T ALLOW MULTIPLE STATUSES --> FIX LATER
				stat = line.split("|")[3]
				stat = stat.split("\n")[0]
				p1_pokemon_status[p1_pokemon_names.index(p1_in_play)] = stat
			elif line[10] == "2":
				#reset p2 pokemon health
				stat = line.split("|")[3]
				stat = stat.split("\n")[0]
				p2_pokemon_status[p2_pokemon_names.index(p2_in_play)] = stat
			else:
				print("SOMETHING HAS GONE WORNG: no player number attatched to status statement")
				print("Tag:  ", line[10])
		if "|turn|" in line:
			game_state = GameState(p2_pokemon_names, p2_pokemon_hp, p2_pokemon_status, p2_action, p2_in_play, p1_pokemon_names, p1_pokemon_hp, p1_pokemon_status, p1_action, p1_in_play, p1_moves, p2_moves)
			game_log.add_state(game_state)
	game_state = GameState(p2_pokemon_names, p2_pokemon_hp, p2_pokemon_status, p2_action, p2_in_play, p1_pokemon_names, p1_pokemon_hp, p1_pokemon_status, p1_action, p1_in_play, p1_moves, p2_moves)
	game_log.add_state(game_state)
	return game_log

def main():
	rootdir = './logs'
	file_list = [f for f in os.listdir('./logs') if os.path.isfile(os.path.join('./logs', f))]
	logs = []
	for file in file_list:
		#Print statements for checking log accuracy
		#print"__________"
		#print file
		#print
		if file == "923289227.txt":
			continue
		else:
			f = open("logs/"+file)
			the_log = readLog(f)
			logs.append(the_log)
		#the_log.printSelf()
		#print
		#print "___________"
	return logs

def test():
	logs = []
	for file in ["920796671.txt", "920938065.txt", "921676011.txt", "921816226.txt"]:
		f = open("logs/"+file)
		the_log = readLog(f)
		logs.append(the_log)
	return logs


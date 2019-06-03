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

#TODO: YOU'RE ACTUALLY ALLOWED TO SEE OPPONENT'S POKEMON
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

#TODO: types not mentioned in log. need a resource to check against

class GameState:
	"""
	A class to hold the features of a turn in a game
	"""
	#Dictionary with pokemon names as keys, [type,hp,status_effects] as values
	# names as keys because multiple pokemon of same type on one team would be confusing

	p2_pokemon_names = []
	p2_pokemon_types = []
	p2_pokemon_hp = []
	p2_pokemon_status = []
	p2_action = None
	#hold index of pokemon currently in play
	p2_in_play = None

	p1_pokemon_names = []
	p1_pokemon_types = []
	p1_pokemon_hp = []
	p1_pokemon_status = []
	p1_action = None
	#hold index of pokemon currently in play
	p1_in_play = None

	def __init__(self, p2_pokemon_names, p2_pokemon_types, p2_pokemon_hp, p2_pokemon_status,
	p2_action, p2_in_play, p1_pokemon_names, p1_pokemon_types, p1_pokemon_hp, p1_pokemon_status,
	p1_action, p1_in_play):
		"""
		Constructor for one gamestate --> state/action pair
		"""	
		self.p2_pokemon_names = p2_pokemon_names
		self.p2_pokemon_types = p2_pokemon_types
		self.p2_pokemon_hp = p2_pokemon_hp
		self.p2_pokemon_status = p2_pokemon_status
		self.p2_action = p2_action
		self.p2_in_play = p2_in_play

		self.p1_pokemon_names = p1_pokemon_names
		self.p1_pokemon_types = p1_pokemon_types
		self.p1_pokemon_hp = p1_pokemon_hp
		self.p1_pokemon_status = p1_pokemon_status
		self.p1_action = p1_action
		self.p1_in_play = p1_in_play

	def update_player_1(pokemon_name,pokemon_type,pokemon_hp,pokemn_status_effects):
		"""
		To be used to backpropogate information
		"""
		if self.p1_pokemon[pokemon_name] == 0:
			self.p1_pokemon[pokemon_name] = [pokemon_type,pokemon_hp,pokemn_status_effects]
	
	#TODO: make get functions




def readLog(text_file):
	log = text_file.readlines()
	p2_pokemon_names = [] 
	p2_pokemon_types = []
	p2_pokemon_hp = []
	p2_pokemon_status = []
	p2_action = None
	p2_in_play = None
	p1_pokemon_names = [] 
	p1_pokemon_types = [] 
	p1_pokemon_hp = [] 
	p1_pokemon_status = []
	p1_action = None
	p1_in_play = None
	game_log = GameLog()

	for line in log:
		if "|poke|p1|" in line: 
			#add pokemon name to p1_names
			line = line[9:]
			name = line.split(",")[0]
			p1_names.append(name)
			#once we know all 6 of p1's pokemon names, add them to game log
			if len(p1_names) == 6 and len(p2_names) == 6:
				game_log.add_start_state(p1_names, p2_names)
		if "|poke|p2|" in line: 
			#add pokemon name to p1_names
			line = line[9:]
			name = line.split(",")[0]
			p2_names.append(name)
			#once we know all 6 of p1's pokemon names, add them to game log
			if len(p1_names) == 6 and len(p2_names) == 6:
				game_log.add_start_state(p1_names, p2_names)
		#TODO: Don't understand how to deal with switching as a turn vs as a bonus action?
		if line[0:8] in "|switch|":
			if line[10] == "1":
				#p1 switched in new pokemon
				line = line[13:]
				line_split = line.split("|")
				current_p1 = line_split[1]

			else if line[10] == "2":
				#p2 switched in new pokemon
				line = line[13:]
				line_split = line.split("|")
				current_p1 = line_split[1]
			else:
				#there was a weird switch I wasn't prepared for, throw an error
				print("SOMETHING HAS GONE WORNG: no player number attatched to switch statement")
		if "|-damage|" in line of "|-heal|" in line:
			#apply damage to hp values
			if line[11] == "1":
				#reset p1 pokemon health
				new_health = line.split("|")
				new_health = new_health[3].split("/")[0]
				p1_pokemon_hp[p1_in_play] = new_health
			else if line[11] == "2":
				#reset p2 pokemon health
				new_health = line.split("|")
				new_health = new_health[3].split("/")[0]
				p2_pokemon_hp[p2_in_play] = new_health
			else:
				print("SOMETHING HAS GONE WORNG: no player number attatched to damage statement")
		if "|-heal|" in line:
			#apply damage to hp values
			if line[9] == "1":
				#reset p1 pokemon health
				new_health = line.split("|")
				new_health = new_health[3].split("/")[0]
				p1_pokemon_hp[p1_in_play] = new_health
			else if line[9] == "2":
				#reset p2 pokemon health
				new_health = line.split("|")
				new_health = new_health[3].split("/")[0]
				p2_pokemon_hp[p2_in_play] = new_health
			else:
				print("SOMETHING HAS GONE WORNG: no player number attatched to damage statement")
		if "|cant|" in line:
			#apply damage to hp values
			if line[8] == "1":
				#reset p1 pokemon health
				p1_action = "None"
			else if line[8] == "2":
				#reset p2 pokemon health
				p2_action = "None"
			else:
				print("SOMETHING HAS GONE WORNG: no player number attatched to damage statement")
		if "|move|" in line:
			#apply damage to hp values
			if line[8] == "1":
				#save move
				move = line.split("|")[3]
				p1_action = move
			else if line[8] == "2":
				#reset p2 pokemon health
				move = line.split("|")[3]
				p2_action = move
			else:
				print("SOMETHING HAS GONE WORNG: no player number attatched to damage statement")
		if "|-status|" in line:
			#apply damage to hp values
			if line[11] == "1":
				#NOTE: THIS DOESN'T ALLOW MULTIPLE STATUSES --> FIX LATER
				stat = line.split("|")[3]
				p1_pokemon_status[p1_in_play] = stat
			else if line[11] == "2":
				#reset p2 pokemon health
				stat = line.split("|")[3]
				p2_pokemon_status[p2_in_play] = stat
			else:
				print("SOMETHING HAS GONE WORNG: no player number attatched to damage statement")
		if "|turn|" in line:
			game_state = GameState(self, p2_pokemon_names, p2_pokemon_types, p2_pokemon_hp, p2_pokemon_status, p2_action, p2_in_play, p1_pokemon_names, p1_pokemon_types, p1_pokemon_hp, p1_pokemon_status, p1_action, p1_in_play):
			game_log.add_state(game_state)




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
		p1_pokemon = {}
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
	p2_pokemon = {}
	p1_pokemon = {}

	def __init__(self, p1_pokemon, p2_pokemon):
		"""
		Constructor for one gamestate
		"""
		self.p1_pokemon = p1_pokemon
		self.p2_pokemon = p2_pokemon

	def update_player_1(pokemon_name,pokemon_type,pokemon_hp,pokemn_status_effects):
		"""
		To be used to backpropogate information
		"""
		if self.p1_pokemon[pokemon_name] == 0:
			self.p1_pokemon[pokemon_name] = [pokemon_type,pokemon_hp,pokemn_status_effects]
	
	#TODO: make get functions




def readLog(text_file):
	log = text_file.readlines()
	p1_names = []
	p2_names = []
	current_p1 = None
	current_p2 = None
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
				current_p1 = line_split[0]

			else if line[10] == "2":
				#p2 switched in new pokemon
			else:
				#there was a weird switch I wasn't prepared for, throw an error

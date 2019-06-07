# This Python file uses the following encoding: utf-8

import database
import itertools
import math
import numpy
import random

class Pokedex:
    # For performance, we define the global average HP as 0 for now. It will be populated
    # automatically the first time it is requested.
    averageHp = 0.0
    
    db = database.connect('pokedex.sqlite')
    
    # Number to type name mapping.
    types = ['Unknown', 'Normal', 'Fighting', 'Flying', 'Poison', 'Ground', 'Rock', 'Bug', 'Ghost', 'Steel', 'Fire', 'Water', 'Grass', 'Electric', 'Psychic', 'Ice', 'Dragon', 'Dark', 'Fairy']
    
    # The National Pokédex numbers of all fully-evolved Pokemon (as of Generation I).
    # https://bulbapedia.bulbagarden.net/wiki/List_of_fully_evolved_Pokémon_by_base_stats
    # 
    # Plus some Pokémon that aren't on that list (because they evolve into Pokémon which were introduced
    # in later generations).
    fullyEvolved = [3, 6, 9, 12, 15, 18, 20, 22, 24, 26, 28, 31, 34, 36, 38, 40, 42, 45, 47, 49, 51, 53, 55, 57, 59, 62, 65, 68, 71, 73, 76, 78, 80, 82, 83, 85, 87, 89, 91, 94, 95, 97, 99, 101, 103, 105, 106, 107, 108, 110, 112, 113, 114, 115, 117, 119, 121, 122, 123, 124, 125, 126, 127, 128, 130, 131, 132, 134, 135, 136, 137, 139, 141, 142, 143, 144, 145, 146, 149, 150, 151]
    
    # Returns basic information about a species (searching by name only)
    @classmethod
    def get(cls, species):
        cursor = cls.db.cursor()
        
        cursor.execute("SELECT * FROM `pokemon_species` WHERE identifier = ? COLLATE NOCASE", (species, ))
        speciesData = cursor.fetchone()
        speciesId = speciesData[0]
        speciesName = str(speciesData[1]).title()
        
        cursor.execute("SELECT * FROM `pokemon_types` WHERE pokemon_id = ?", (speciesId, ))
        speciesTypes = [cls.types[record[1]] for record in cursor.fetchall()]
        
        return {
            'id': speciesId,
            'name': speciesName,
            'type': tuple(speciesTypes),
            'averageHp': cls.getAverageHp(speciesId)
        }
    
    @classmethod
    def search(cls, species):
        cursor = cls.db.cursor()
        
        cursor.execute("SELECT * FROM `pokemon_species` WHERE id = ?", (species, ))
        speciesData = cursor.fetchone()
        speciesId = speciesData[0]
        speciesName = str(speciesData[1]).title()
        
        cursor.execute("SELECT * FROM `pokemon_types` WHERE pokemon_id = ?", (speciesId, ))
        speciesTypes = [cls.types[record[1]] for record in cursor.fetchall()]
        
        return {
            'id': speciesId,
            'name': speciesName,
            'type': tuple(speciesTypes),
            'averageHp': cls.getAverageHp(speciesId)
        }
    
    # Computes the expected HP value of a given species - or all fully-evolved species if
    # no species is given (under the assumption that one will be chosen at random).
    @classmethod
    def getAverageHp(cls, species = None):
        if species is None:
            if cls.averageHp == 0.0:
                speciesHp = [cls.getAverageHp(id) for id in cls.fullyEvolved]
                cls.averageHp = numpy.mean(speciesHp)
            return cls.averageHp
        elif isinstance(species, (int, long)):
            cursor = cls.db.cursor()
            cursor.execute("SELECT * FROM `pokemon_stats` WHERE pokemon_id = ? AND stat_id = 1", (species, ))
            speciesData = cursor.fetchone()
            base = speciesData[2]
            
            points = 0
            for iv in range(16):
                for ev in range(65):
                    # Calculate an HP stat possibility given an "EV", IV, and base stat combination.
                    # From https://bulbapedia.bulbagarden.net/wiki/Statistic#In_Generations_I_and_II
                    # Some simplifications have been made to help with the math.
                    stat = math.floor((base + iv) * 2 + ev) + 110
                    
                    # Add the stat value to the possibilities with the correct distribution.
                    minEv = math.pow((ev * 4) - 1, 2) if ev > 0 else 0
                    maxEv = math.pow((ev * 4) + 3, 2) if ev < 64 else 65535
                    count = int(maxEv - minEv)
                    points += count * stat
            return float(points) / 1048560.0
        else:
            speciesData = cls.get(species)
            return cls.getAverageHp(speciesData['id'])

    # Computes the probability that an unknown Pokémon knows a move that is super effective against
    # a given type combination.
    @classmethod
    def getProbabilityWeakToUnknown(cls, types, species = None):
        if species is None:
            speciesProbability = [cls.getProbabilityWeakToUnknown(types, id) for id in cls.fullyEvolved]
            return numpy.mean(speciesProbability)
        elif isinstance(species, (int, long)):            
            typeDistrib = list(numpy.zeros(19, dtype=int))
            damagingTypeDistrib = list(numpy.zeros(19, dtype=int))
            
            for move in cls.getLegalMoves(species):
                typeDistrib[move['type_id']] += 1
                if move['power'] is not None:
                    damagingTypeDistrib[move['type_id']] += 1
            
            numberStrongMoves = 0
            for typeIndex in range(1, 16):
                if cls.getTypeEffectiveness(cls.types[typeIndex], types) > 1:
                    numberStrongMoves += damagingTypeDistrib[typeIndex]
            
            numberMoves = max(numpy.sum(typeDistrib), 4)
            
            probability = 1 - float(len(list(itertools.combinations(range(numberMoves - numberStrongMoves), 4)))) / float(len(list(itertools.combinations(range(numberMoves), 4))))
            
            return probability
        else:
            speciesData = cls.get(species)
            return cls.getProbabilityWeakToUnknown(types, speciesData['id'])
    
    @classmethod
    def getProbabilityStrongAgainstUnknown(cls, moveTypes, species = None):
        if species is None:
            speciesProbability = [cls.getProbabilityStrongAgainstUnknown(moveTypes, id) for id in cls.fullyEvolved]
            return numpy.mean(speciesProbability)
        elif isinstance(species, (int, long)):
            cursor = cls.db.cursor()
            cursor.execute("SELECT * FROM `pokemon_types` WHERE pokemon_id = ?", (species, ))
            speciesTypes = tuple([cls.types[record[1]] for record in cursor.fetchall()])
            uniqueMoveTypes = list(numpy.unique(numpy.array(moveTypes)))
            
            for type in uniqueMoveTypes:
                if cls.getTypeEffectiveness(type, speciesTypes) > 1:
                    return 1.0
            
            return 0.0
        else:
            speciesData = cls.get(species)
            return cls.getProbabilityWeakToUnknown(moveTypes, speciesData['id'])
    
    @classmethod
    def getTypeEffectiveness(cls, attack, defense):
        if isinstance(defense, (str, basestring)) or len(defense) == 1:
            attackType = cls.types.index(attack)
            defenseType = cls.types.index(defense[0]) if isinstance(defense, tuple) else cls.types.index(defense)
            cursor = cls.db.cursor()
            cursor.execute("SELECT * FROM type_efficacy WHERE damage_type_id = ? AND target_type_id = ?", (attackType, defenseType))
            return cursor.fetchone()[2]
        else:
            return cls.getTypeEffectiveness(attack, defense[0]) * cls.getTypeEffectiveness(attack, defense[1]) / 10000.0
            
    @classmethod
    def getLegalMoves(cls, species):
        if isinstance(species, (int, long)):
            cursor = cls.db.cursor()
            
            # This database query selects all legal moves that a Pokémon is allowed to learn and returns
            # them, along with additional metadata, in one combined table (for performance reasons).
            # 
            # pokemon_moves stores the list of moves that Pokémon can learn in each game set; we force
            # the game to use the Red/Blue/Yellow set with "pokemon_moves.version_group_id = 1" in the
            # WHERE clause.
            # 
            # INNER JOIN moves ON moves.id = pokemon_moves.move_id
            #   This adds additional move data such as power, accuracy, and move type.
            #   
            # INNER JOIN move_names ON move_names.move_id = moves.id
            #   This allows the "display" name of a move to be returned.
            #   (Filtered to English with "move_names.local_language_id = 9" in the WHERE clause)
            cursor.execute("SELECT pokemon_moves.*, moves.*, move_names.* FROM pokemon_moves INNER JOIN moves ON moves.id = pokemon_moves.move_id INNER JOIN move_names ON move_names.move_id = moves.id WHERE pokemon_moves.pokemon_id = ? AND pokemon_moves.version_group_id = 1 AND move_names.local_language_id = 9 GROUP BY pokemon_moves.move_id", (species, ))
            
            return [{
                'name': str(move[23]),
                'id': move[0],
                'type': cls.types[move[9]],
                'type_id': move[9],
                'power': move[10],
                'pp': move[11],
                'accuracy': move[12]
            } for move in cursor.fetchall()]
        else:
            speciesData = cls.get(species)
            return cls.getLegalMoves(speciesData['id'])

    @classmethod
    def getMove(cls, name):
        nameKebab = name.lower().replace(' ', '-')
        cursor = cls.db.cursor()
        
        cursor.execute("SELECT * FROM `moves` WHERE identifier = ? COLLATE NOCASE", (nameKebab, ))
        moveData = cursor.fetchone()
        
        return {
            'id': moveData[0],
            'name': name,
            'type': cls.types[moveData[3]],
            'power': moveData[4],
            'pp': moveData[5],
            'accuracy': moveData[6],
            'priority': moveData[7],
            'effect_id': moveData[10],
            'effect_prob': moveData[11]
        }
        
    @classmethod
    def randomTeam(cls):
        species = []
        while len(species) < 6:
            choice = random.choice(cls.fullyEvolved)
            if choice not in species:
                species.append(choice)
        
        team = []
        for pokemon in species:
            moves = cls.getLegalMoves(pokemon)
            movesetLength = min(len(moves), 4)
            moveset = []
            while len(moveset) < movesetLength:
                choice = random.choice(moves)
                if choice not in moveset:
                    moveset.append(choice)
            speciesData = cls.search(pokemon)
            speciesData['moves'] = moveset
            team.append(speciesData)
        
        return team
            
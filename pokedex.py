# This Python file uses the following encoding: utf-8

import database
import math
import numpy

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
    
    # Returns basic information about a species.
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
            return cls.getAverageHp(speciesData.id)

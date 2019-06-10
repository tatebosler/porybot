Porybot: A (Sad) Attempt of Intelligent Pokémon Battling
Tate Bosler '19 and Laura DeMane '19

Dependencies: sqlite3, itertools, numpy, math, random, sys, os
(Python package management sucks, but these should be available in most installations.)

To execute the program and simulate a battle against itself:
- python porybot.py

OPTIONS:
- --interactive: Allows human control of the first player.
                 (Otherwise, the first player will play using the Q-learned weights.)
- --num-games=N: How many games should be played.
- --random:      Causes the second player to randomly choose moves each turn and never switch.
                 (Otherwise, the second player will play using the Q-learned weights.)

Files worth reading:
- porybot.py
- AIfinallogreader.py
- QLearner.py

Files used as utility classes:
- pokedex.py
- database.py

Logs have been updated for battles up to 2:00 pm Monday, June 10. If you need even
newer logs, you'll need PHP 7 and Composer, and run the following commands from the
root of the project (in order):
- cd retriever
- composer install (or `php composer.phar install` if you've installed Composer locally)
- php cron.php
- cp logs/*.txt ../logs/
- grep -l Ditto ../logs/* | xargs rm

Formulas for damage calculation and other data sourced from the Bulbapedia editors:
- https://bulbapedia.bulbagarden.net/wiki/Damage
- https://bulbapedia.bulbagarden.net/wiki/Statistic
- https://bulbapedia.bulbagarden.net/wiki/Type/Type_chart#Generation_I

Database used in this project sourced from Veekun:
- https://veekun.com/dex/downloads#other-files

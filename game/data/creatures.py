player: dict = {
    "name": "Player",
    "char": '@',
    "color": "blue",
    "hp": 500,
    "mp": 500,
    "dmg": 5
}

enemies: dict[str, dict] = {
    # Rare enemies (spawn % <10).
    "vampire": {
        "name": "Vampire",
        "char": "V",
        "color": "magenta",
        "hp": 40,
        "dmg": 6,
        "spawn_chance": 9,  # out of 100, relative weight percentage
        "energy": 9  # 10 is full energy for reference
    },
    "jotnar": {
        "name": "Jotnar",
        "char": "J",
        "color": "grey",
        "hp": 60,
        "dmg": 8,
        "spawn_chance": 6,
        "energy": 4
    },
    "mimic": {
        "name": "Mimic",
        "char": "m",
        "color": "brown",
        "hp": 20,
        "dmg": 7,
        "spawn_chance": 5,
        "energy": 5
    },
    "automaton": {
        "name": "Automaton",
        "char": "A",
        "color": "yellow",
        "hp": 55,
        "dmg": 7,
        "spawn_chance": 7,
        "energy": 5
    },
    
    # Medium rare enemies (spawn % >=10 & <25).
    "wraith": {
        "name": "Wraith",
        "char": "w",
        "color": "cyan",
        "hp": 25,
        "dmg": 7,
        "spawn_chance": 17,
        "energy": 9
    },
    "ghoul": {
        "name": "Ghoul",
        "char": 'g',
        "color": "red",
        "hp": 28,
        "dmg": 5,
        "spawn_chance": 19,
        "energy": 9
    },
    "insectoid": {
        "name": "Insectoid",
        "char": 'i',
        "color": "green",
        "hp": 35,
        "dmg": 6,
        "spawn_chance": 20,
        "energy": 9
    },
    "elemental": {
        "name": "Elemental",
        "char": 'e',
        "color": "brown",
        "hp": 20,
        "dmg": 6,
        "spawn_chance": 19,
        "energy": 7
    },
    "golem": {
        "name": "Golem",
        "char": 'g',
        "color": "grey",
        "hp": 40,
        "dmg": 6,
        "spawn_chance": 15,
        "energy": 5
    },
    
    # Well-done enemies (spawn % >= 25 and up).
    "giant_rat": {
        "name": "Giant Rat",
        "char": "r",
        "color": "grey",
        "hp": 10,
        "dmg": 4,
        "spawn_chance": 35,
        "energy": 8
    },
    "troll": {
        "name": "Troll",
        "char": "t",
        "color": "green",
        "hp": 30,
        "dmg": 6,
        "spawn_chance": 40,
        "energy": 7
    },
    "arachnid": {
        "name": "Arachnid",
        "char": "s",
        "color": "grey",
        "hp": 10,
        "dmg": 7,
        "spawn_chance": 20,
        "energy": 8
    },
    "imp": {
        "name": "Imp",
        "char": "i",
        "color": "grey",
        "hp": 15,
        "dmg": 5,
        "spawn_chance": 35,
        "energy": 7
    },
    "chirofling": {
        "name": "Chirofling",
        "char": "b",
        "color": "brown",
        "hp": 15,
        "dmg": 5,
        "spawn_chance": 40,
        "energy": 9
    },
    "draugr": {
        "name": "Draugr",
        "char": "d",
        "color": "off_white",
        "hp": 25,
        "dmg": 5,
        "spawn_chance": 23,
        "energy": 7
    },
    "basilisk": {
        "name": "Basilisk",
        "char": "b",
        "color": "forest_green",
        "hp": 18,
        "dmg": 5,
        "spawn_chance": 38,
        "energy": 7
    },
    "kobold": {
        "name": "Kobold",
        "char": "k",
        "color": "off_white",
        "hp": 20,
        "dmg": 6,
        "spawn_chance": 35,
        "energy": 7
    },
    "gel": {
        "name": "Gel",
        "char": "g",
        "color": "white",
        "hp": 23,
        "dmg": 5,
        "spawn_chance": 35,
        "energy": 6
    },
    
    # Meme.
    "jhermayne": {
        "name": "Jhermayne",
        "char": "J",
        "color": "yellow",
        "hp": 1,
        "dmg": 99,
        "spawn_chance": 1,
        "energy": 5
    },
}
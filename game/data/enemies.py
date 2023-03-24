enemies: dict[str, dict] = {
    "ghoul": {
        "name": "Ghoul",
        "char": 'g',
        "color": "red",
        "hp": 35,
        "dmg": 5,
        "spawn_chance": 33,  # out of 100, relative weight percentage
        "energy": 9  # 10 is full energy for reference
    },
    "giant_rat": {
        "name": "Giant Rat",
        "char": "r",
        "color": "grey",
        "hp": 10,
        "dmg": 3,
        "spawn_chance": 45,
        "energy": 8
    },
    "vampire": {
        "name": "Vampire",
        "char": "V",
        "color": "magenta",
        "hp": 40,
        "dmg": 6,
        "spawn_chance": 20,
        "energy": 9
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
    "wraith": {
        "name": "Wraith",
        "char": "w",
        "color": "cyan",
        "hp": 25,
        "dmg": 7,
        "spawn_chance": 25,
        "energy": 9
    },
    "giant_spider": {
        "name": "Giant Spider",
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
        "color": "green",
        "hp": 15,
        "dmg": 5,
        "spawn_chance": 45,
        "energy": 7
    },
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
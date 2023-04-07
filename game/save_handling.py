from __future__ import annotations

import pickle
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Union, Any, Optional

if TYPE_CHECKING:
    from pathlib import Path
    from .engine import Engine

from .spawner import Spawner
from .entities import Player
from .dungeon.dungeon import Dungeon
from .message_log import MessageLog
from .data.config import *


@dataclass
class Save:
    """Encapsulates the savegame data and metadata"""
    slot_index: int
    path: Optional[Path]
    data: Optional[dict[str, Any]]
    metadata: Optional[dict[str, Any]]
    
    @property
    def is_empty(self) -> bool:
        return (
            self.slot_index == -1
            and self.path is None
            and self.data is None
            and self.metadata is None
        )


def get_new_game(slot_index: int) -> Save:
    """Create a fresh game"""
    spawner = Spawner()
    player: Player = spawner.get_player_instance()
    dungeon = Dungeon(
        spawner=spawner,
        num_floors=NUM_FLOORS,
        max_enemies_per_floor=MAX_ENEMIES_PER_FLOOR,
        floor_dimensions=FLOOR_DIMENSIONS,
        min_max_rooms=MIN_MAX_ROOMS,
        min_max_room_width=MIN_MAX_ROOM_WIDTH,
        min_max_room_height=MIN_MAX_ROOM_HEIGHT
    )
    message_log = MessageLog()
    time_created: datetime = datetime.now()

    return Save(
        slot_index=slot_index,
        path=None,
        data={
            "player": player,
            "dungeon": dungeon,
            "message_log": message_log
        },
        metadata={
            "created_at": time_created,
            "last_played": time_created,
            # TODO add game version
        }
    )


def is_valid_save(save: Save) -> bool:
    """Peek at its contents and ensure it's a valid savefile for the game"""
    return (
        isinstance(save.data.get("dungeon"), Dungeon)
        and isinstance(save.data.get("player"), Player)
        and isinstance(save.data.get("message_log"), MessageLog)
        and isinstance(save.metadata.get("created_at"), datetime)
        and isinstance(save.metadata.get("last_played"), datetime)
    )


def fetch_saves(saves_dir: Path) -> list[Save]:
    """Fetch savefiles from the saves directory"""
    if not saves_dir.exists():  # Ensure there is a save directory.
        saves_dir.mkdir()
        
    saves: list[Save] = []
    for path in saves_dir.glob("*.sav"):
        with open(path, "rb") as f:
            save: Save = pickle.load(f)
            assert is_valid_save(save)
            saves.append(save)

            if len(saves) >= 5:  # Display only 5 valid saves.
                break
    
    # Fill empty slots.
    while len(saves) < 5:
        saves.append(Save(-1, None, None, None))

    return saves


def fetch_save(saves: list[Save], index: int) -> Save:
    """Load and return the savedata from a selected savefile"""
    save: Save = saves[index]
    if save.is_empty:
        return save
    with open(save.path, "rb") as f:
        save: Save = pickle.load(f)
        assert is_valid_save(save)
        
    return save


# TODO overwrite selected savefile via index
def create_new_save(engine: Engine, saves_dir: Path, index: int) -> None:
    """Create a save file in the saves directory"""
    saves_dir.mkdir(parents=True, exist_ok=True)
    
    occupied_save: Save = fetch_saves(saves_dir)[index]
    if not occupied_save.is_empty:
        path: Path = occupied_save.path
        if path.exists():
            path.unlink()
    
    path = saves_dir / "mysave.sav"
    duplicate_index: int = 1
    while path.exists():
        path = saves_dir / f"mysave({duplicate_index}).sav"
        duplicate_index += 1
    
    with open(path, "wb") as f:
        # pickle.dump(get_new_game())
        pickle.dump(
            Save(
                slot_index=index,
                path=path,
                data={
                    "player": engine.player,
                    "dungeon": engine.dungeon,
                    "message_log": engine.message_log
                },
                metadata={
                    "created_at": engine.save_meta.get("created_at"),
                    "last_played": engine.save_meta.get("last_played")
                }
            ),
            f
        )


# def overwrite_save(index: int):
#     pass


def delete_save(save: Save) -> None:
    pass

    
from __future__ import annotations

import pickle
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

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
            self.path is None
            and self.data is None
            and self.metadata is None
        )
    
    @classmethod
    def get_empty(cls) -> Save:
        return cls(-1, None, None, None)


def get_new_game(slot_index: int) -> Save:
    """Create a fresh game"""
    spawner = Spawner()
    player: Player = spawner.get_player_instance()
    dungeon = Dungeon(
        spawner=spawner,
        num_floors=NUM_FLOORS,
        max_enemies_per_floor=MAX_ENEMIES_PER_FLOOR,
        max_items_per_floor=MAX_ITEMS_PER_FLOOR,
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
    indices_inside: set[int] = set()  # Tracking which slot indices are filled.
    for path in saves_dir.glob("*.sav"):
        with open(path, "rb") as f:
            save: Save = pickle.load(f)
            try:
                assert is_valid_save(save)
            except AssertionError:
                raise Exception("Corrupted save")
            saves.append(save)
            indices_inside.add(save.slot_index)

            if len(saves) >= 5:  # Display only 5 valid saves.
                break
    
    # Order the save slots by their indices.
    for i in range(5):
        if i in indices_inside:
            continue
        saves.append(Save(i, None, None, None))
    saves.sort(key=lambda save: save.slot_index)

    return saves


def fetch_save(saves: list[Save], index: int) -> Save:
    """Load and return the savedata from a selected savefile"""
    save: Save = saves[index]
    if save.is_empty:
        return save
    try:
        with open(save.path, "rb") as f:
            save: Save = pickle.load(f)
            assert is_valid_save(save)
    except FileNotFoundError:
        return Save.get_empty()
        
    return save


def get_current_save_data(engine: Engine) -> Save:
    """Fetch the current game data from the engine and into a save object"""
    return Save(
        slot_index=engine.save.slot_index,
        path=engine.save.path,
        data=engine.save.data,
        metadata=engine.save.metadata
    )


def save_current_game(engine: Engine) -> None:
    """Save filedata from the currently-played game"""
    current_savegame: Save = get_current_save_data(engine)
    current_savegame.metadata["last_played"] = datetime.now()  # Update time.

    with open(current_savegame.path, "wb") as f:
        pickle.dump(current_savegame, f)


def save_to_dir(saves_dir: Path, index: int, save: Save) -> None:
    """Save file data given a save in the saves directory"""
    saves_dir.mkdir(parents=True, exist_ok=True)
    
    # Overwrite save if selected an occupied save.
    occupied_save: Save = fetch_saves(saves_dir)[index]
    delete_save_slot(occupied_save)
    
    path = saves_dir / "mysave.sav"
    duplicate_index: int = 1
    while path.exists():
        path = saves_dir / f"mysave({duplicate_index}).sav"
        duplicate_index += 1
    
    # Update path.
    save.path = path
    with open(path, "wb") as f:
        pickle.dump(save, f)


def delete_save_slot(save: Save) -> None:
    if not save.is_empty:
        path: Path = save.path
        if path.exists():
            path.unlink()

    
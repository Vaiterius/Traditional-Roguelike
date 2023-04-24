from collections import deque
from enum import Enum, auto


class MessageType(Enum):
    INFO = auto()
    PLAYER_ATTACK = auto()
    ENEMY_ATTACK = auto()


class Message:
    """Hold message content and other relevant info"""
    
    def __init__(self,
                 message: str,
                 type: MessageType,
                 debug: bool,
                 color: str):
        self.message = message
        self.type = type
        self.debug = debug
        self.color = color
        
        self.chained_messages: int = 0
        self.count: int = 1
        
        if debug:
            self.message = "[DEBUG] " + self.message
    
    
    def __str__(self):
        if self.count > 1:
            return f"{self.message} x{self.count}"
        return self.message


class MessageLog:
    """Message logger for game display"""
    
    MAX_CHAINS: int = 2  # Can only attach to two other messages.
    START_MESSAGE = Message(
        message="Welcome to <unnamed game>!",
        type=MessageType.INFO,
        debug=False,
        color="blue"
    )
    
    def __init__(self):
        self.messages: deque = deque([self.START_MESSAGE])
        self.history: deque = deque([self.START_MESSAGE])    
    
    @property
    def size(self) -> int:
        return len(self.messages)
    
    @property
    def prev_message(self) -> str:
        return self.messages[0]
    
    
    def get(self, index: int) -> str:
        return self.messages[index]


    def add(self,
            message: str,
            type: str = MessageType.INFO,
            debug: bool = False,
            color: str = "") -> None:
        if isinstance(message, int):
            message = str(message)

        new_message = Message(message, type, debug, color)
        
        # TODO make message type enum.
        # Chain attack messages together.
        if (
            self.prev_message.type == MessageType.PLAYER_ATTACK
            and new_message.type == MessageType.ENEMY_ATTACK
            and self.prev_message.chained_messages < self.MAX_CHAINS
        ):
            self.prev_message.message += "; " + new_message.message
            self.prev_message.chained_messages += 1
            return
        
        # Message is the same as the previous.
        if new_message.message == self.prev_message.message:
            self.messages[0].count += 1
            return

        self.messages.appendleft(new_message)
        self.history.appendleft(new_message)
    
    
    def clear(self) -> None:
        self.messages = deque([self.START_MESSAGE])
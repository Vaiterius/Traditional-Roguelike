from collections import deque


class Message:
    """Hold message content and other relevant info"""
    
    def __init__(self, message: str, debug: bool = False, color: str = ""):
        self.message = message
        self.debug = debug
        self.color = color
        self.count = 1
        
        if debug:
            self.message = "[DEBUG] " + self.message
    
    
    def __str__(self):
        if self.count > 1:
            return f"{self.message} x{self.count}"
        return self.message


class MessageLog:
    """Message logger for game display"""
    
    START_MESSAGE = Message("Welcome to <unnamed game>!", color="blue")
    
    def __init__(self):
        self.messages: deque = deque([self.START_MESSAGE])
        self.history: deque = deque([self.START_MESSAGE])
    
    
    def get(self, index: int) -> str:
        return self.messages[index]
    
    
    def size(self) -> int:
        return len(self.messages)


    def add(self, message: str, debug: bool = False, color: str = "") -> None:
        if isinstance(message, int):
            message = str(message)

        new_message = Message(message, debug, color)    
        
        # Message is the same as the previous.
        if new_message.message == self.messages[0].message:
            self.messages[0].count += 1
            return

        self.messages.appendleft(new_message)
        self.history.appendleft(new_message)
    
    
    def clear(self) -> None:
        self.messages = deque([self.START_MESSAGE])
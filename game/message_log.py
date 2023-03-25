from collections import deque


class Message:
    """Hold message content and other relevant info"""
    
    def __init__(self, message: str):
        self.message = message
        self.count = 1
    
    
    def __str__(self):
        if self.count > 1:
            return f"{self.message} x{self.count}"
        return self.message


class MessageLog:
    """Message logger for game display"""
    GREETING_MESSAGE = "Welcome to <unnamed game>!"
    
    def __init__(self):
        self.messages: deque = deque([Message(self.GREETING_MESSAGE)])
        self.history: deque = deque([Message(self.GREETING_MESSAGE)])
    
    
    def get(self, index: int) -> str:
        return self.messages[index]
    
    
    def size(self) -> int:
        return len(self.messages)


    def add(self, message: str, debug: bool = False) -> None:
        if isinstance(message, int):
            message = str(message)

        if debug:
            message = "[DEBUG] " + message
        
        new_message = Message(message)    
        
        # Message is the same as the previous.
        if new_message.message == self.messages[0].message:
            self.messages[0].count += 1
            return

        self.messages.appendleft(new_message)
        self.history.appendleft(new_message)
    
    
    def clear(self) -> None:
        self.messages = deque([Message(self.GREETING_MESSAGE)])
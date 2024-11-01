from enum import Enum


class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LOCATION = "location"



class ChatType(Enum):
    PRIVATE = "private"
    GROUP = "group"
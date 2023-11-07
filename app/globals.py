# Global constants and Enums
from enum import Enum

class Role(Enum):
    USER = 0
    ORGANIZER = 1

EVENT_CATEGORIES = ["Academic", "Hobbies", "Music", "Nightlife", "Business"]
# List of tags that can be used to sort the event data
# NOTE: Do not add a tag named "clear", since it has a special functionality
FILTERS = ["In-Person", "Today", "Free", *EVENT_CATEGORIES]

DB_NAME = "database.db"
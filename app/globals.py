# Global constants and Enums
from enum import Enum

class Role(Enum):
    USER = 0
    ORGANIZER = 1

DB_NAME = "database.db"
FILTERS = ['In-Person', 'Today', 'Free', 'Music']
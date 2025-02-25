# family_connections/detector.py

from datetime import datetime
from typing import List, Dict
from thefuzz import fuzz
from geopy.distance import geodesic

class FamilyConnectionDetector:
    """
    A class to detect potential family connections between corporate officers.
    
    Attributes:
        SURNAME_SIMILARITY_THRESHOLD (int): Minimum percentage for surname matching
        MIDDLE_NAME_MATCH_SCORE (int): Points awarded for shared middle names
        SIBLING_AGE_RANGE (int): Maximum age difference for potential siblings
        GENERATIONAL_AGE_GAP (int): Typical age difference for parent-child relationships
        ADDRESS_PROXIMITY_THRESHOLD (float): Maximum distance (miles) for nearby addresses

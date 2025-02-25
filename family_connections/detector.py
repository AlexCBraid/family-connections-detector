# family_connections/detector.py

from datetime import datetime
from typing import List, Dict
from thefuzz import fuzz
try:
    from geopy.distance import geodesic
except ImportError:
    # Fallback if geopy is not installed
    def geodesic(coord1, coord2):
        class Result:
            def __init__(self, miles=float('inf')):
                self.miles = miles
        return Result()

class FamilyConnectionDetector:
    """
    A class to detect potential family connections between corporate officers.
    
    Attributes:
        SURNAME_SIMILARITY_THRESHOLD (int): Minimum percentage for surname matching
        MIDDLE_NAME_MATCH_SCORE (int): Points awarded for shared middle names
        SIBLING_AGE_RANGE (int): Maximum age difference for potential siblings
        GENERATIONAL_AGE_GAP (int): Typical age difference for parent-child relationships
        ADDRESS_PROXIMITY_THRESHOLD (float): Maximum distance (miles) for nearby addresses
        COMPANY_NAME_SCORE (int): Points for surname appearing in company name
        MULTIPLE_ROLES_SCORE (int): Points for holding multiple roles
        APPOINTMENT_TIMING_THRESHOLD (int): Days threshold for synchronized appointments
        APPOINTMENT_TIMING_SCORE (int): Points for synchronized appointments
        RESIGNATION_TIMING_SCORE (int): Points for synchronized resignations
        SHARED_ADDRESS_SCORE (int): Points for exact same address
        NEARBY_ADDRESS_SCORE (int): Points for addresses within proximity threshold
    """
    
    def __init__(self, **kwargs):
        # Default configuration parameters
        self.SURNAME_SIMILARITY_THRESHOLD = kwargs.get('surname_similarity_threshold', 85)
        self.MIDDLE_NAME_MATCH_SCORE = kwargs.get('middle_name_match_score', 25)
        self.SIBLING_AGE_RANGE = kwargs.get('sibling_age_range', 3)
        self.GENERATIONAL_AGE_GAP = kwargs.get('generational_age_gap', 30)
        self.ADDRESS_PROXIMITY_THRESHOLD = kwargs.get('address_proximity_threshold', 1)
        self.COMPANY_NAME_SCORE = kwargs.get('company_name_score', 35)
        self.MULTIPLE_ROLES_SCORE = kwargs.get('multiple_roles_score', 20)
        self.APPOINTMENT_TIMING_THRESHOLD = kwargs.get('appointment_timing_threshold', 90)
        self.APPOINTMENT_TIMING_SCORE = kwargs.get('appointment_timing_score', 25)
        self.RESIGNATION_TIMING_SCORE = kwargs.get('resignation_timing_score', 25)
        self.SHARED_ADDRESS_SCORE = kwargs.get('shared_address_score', 40)
        self.NEARBY_ADDRESS_SCORE = kwargs.get('nearby_address_score', 20)
        
    def calculate_connection_score(self, person1: Dict, person2: Dict) -> Dict:
        """
        Calculate a connection score between two people based on various factors.
        Returns a dictionary with individual scores and reasoning.
        
        Args:
            person1: Dictionary with first person's data
            person2: Dictionary with second person's data
            
        Returns:
            Dictionary with total score, reasons and confidence level
        """
        scores = {
            'total_score': 0,
            'reasons': [],
            'confidence': 'LOW'
        }
        
        # 1. Check full name similarity (including middle names)
        name_scores = self._check_name_similarity(
            person1.get('full_name', ''),
            person2.get('full_name', ''),
            person1.get('middle_names', []),
            person2.get('middle_names', [])
        )
        
        if name_scores.get('surname_score', 0) > 0:
            scores['reasons'].append(f"Surname similarity: {name_scores['surname_score']}%")
            scores['total_score'] += name_scores['surname_score']
            
        if name_scores.get('middle_name_score', 0) > 0:
            scores['reasons'].append(f"Shared middle name: {name_scores['middle_name_score']} points")
            scores['total_score'] += name_scores['middle_name_score']
        
        # 2. Check age relationships
        if 'date_of_birth' in person1 and 'date_of_birth' in person2:
            age_score = self._check_age_relationship(
                person1['date_of_birth'],
                person2['date_of_birth']
            )
            if age_score > 0:
                scores['reasons'].append(f"Age relationship match: {age_score} points")
                scores['total_score'] += age_score
        
        # 3. Check shared appointments and multiple roles
        appointment_scores = self._check_appointments(
            person1.get('roles', []),
            person2.get('roles', [])
        )
        
        if appointment_scores.get('shared_score', 0) > 0:
            scores['reasons'].append(f"Shared appointments: {appointment_scores['shared_score']} points")
            scores['total_score'] += appointment_scores['shared_score']
            
        if appointment_scores.get('multiple_roles_score', 0) > 0:
            scores['reasons'].append(f"Multiple roles held: {appointment_scores['multiple_roles_score']} points")
            scores['total_score'] += appointment_scores['multiple_roles_score']
            
        if appointment_scores.get('timing_score', 0) > 0:
            scores['reasons'].append(f"Synchronized appointments/resignations: {appointment_scores['timing_score']} points")
            scores['total_score'] += appointment_scores['timing_score']
        
        # 4. Check PSC overlap
        psc_score = self._check_psc_overlap(
            person1.get('psc_holdings', []),
            person2.get('psc_holdings', [])
        )
        if psc_score > 0:
            scores['reasons'].append(f"PSC overlap: {psc_score} points")
            scores['total_score'] += psc_score
        
        # 5. Check address proximity
        address_scores = self._check_address_proximity(
            person1.get('address', {}),
            person2.get('address', {})
        )
        
        if address_scores.get('exact_match_score', 0) > 0:
            scores['reasons'].append(f"Exact address match: {address_scores['exact_match_score']} points")
            scores['total_score'] += address_scores['exact_match_score']
            
        if address_scores.get('proximity_score', 0) > 0:
            scores['reasons'].append(f"Address proximity: {address_scores['proximity_score']} points")
            scores['total_score'] += address_scores['proximity_score']
        
        # 6. Check if surname appears in company name
        company_name_score = self._check_surname_in_company_name(
            person1.get('surname', ''),
            person1.get('company_name', '')
        )
        if company_name_score > 0:
            scores['reasons'].append(f"Surname found in company name: {company_name_score} points")
            scores['total_score'] += company_name_score
        
        # Set confidence level based on total score
        scores['confidence'] = self._determine_confidence(scores['total_score'])
        return scores
    
    def _check_name_similarity(self, name1: str, name2: str, 
                             middle_names1: List[str], middle_names2: List[str]) -> Dict:
        """
        Enhanced name checking that includes middle name matching.
        
        Args:
            name1: Full name of first person
            name2: Full name of second person
            middle_names1: List of middle names for first person
            middle_names2: List of middle names for second person
            
        Returns:
            Dictionary with surname similarity score and middle name match score
        """
        result = {
            'surname_score': 0,
            'middle_name_score': 0
        }
        
        # Extract surnames
        surname1 = name1.split()[-1].lower() if name1 else ''
        surname2 = name2.split()[-1].lower() if name2 else ''
        
        # Check surname similarity
        if surname1 and surname2:
            similarity = fuzz.ratio(surname1, surname2)
            if similarity >= self.SURNAME_SIMILARITY_THRESHOLD:
                result['surname_score'] = similarity
        
        # Check middle names
        if middle_names1 and middle_names2:
            shared_middle_names = set(m.lower() for m in middle_names1) & set(m.lower() for m in middle_names2)
            if shared_middle_names:
                result['middle_name_score'] = self.MIDDLE_NAME_MATCH_SCORE * len(shared_middle_names)
        
        return result
    
    def _check_age_relationship(self, dob1: str, dob2: str) -> int:
        """
        Check if age difference suggests a family relationship.
        
        Args:
            dob1: Date of birth for first person (YYYY-MM-DD)
            dob2: Date of birth for second person (YYYY-MM-DD)
            
        Returns:
            Score based on age relationship type (sibling/parent-child)
        """
        try:
            date1 = datetime.strptime(dob1, '%Y-%m-%d')
            date2 = datetime.strptime(dob2, '%Y-%m-%d')
            
            age_diff = abs((date1 - date2).days / 365.25)
            
            if age_diff <= self.SIBLING_AGE_RANGE:
                return 30  # High points for potential siblings
            elif abs(age_diff - self.GENERATIONAL_AGE_GAP) <= 5:
                return 25  # Points for potential parent-child
            
            return 0
            
        except ValueError:
            return 0  # Return 0 if dates can't be parsed
    
    def _check_appointments(self, roles1: List[Dict], roles2: List[Dict]) -> Dict:
        """
        Enhanced appointment checking that includes multiple role detection
        and appointment timing analysis.
        
        Args:
            roles1: List of roles for first person
            roles2: List of roles for second person
            
        Returns:
            Dictionary with shared appointment score, multiple roles score, and timing score
        """
        result = {
            'shared_score': 0,
            'multiple_roles_score': 0,
            'timing_score': 0
        }
        
        if not roles1 or not roles2:
            return result
            
        # Check for shared appointments
        companies1 = set(role['company_number'] for role in roles1)
        companies2 = set(role['company_number'] for role in roles2)
        shared_companies = companies1.intersection(companies2)
        result['shared_score'] = len(shared_companies) * 15  # 15 points per shared company
        
        # Check for multiple roles
        roles_count1 = len(set(role['role_type'] for role in roles1))
        roles_count2 = len(set(role['role_type'] for role in roles2))
        
        if roles_count1 > 1:
            result['multiple_roles_score'] += self.MULTIPLE_ROLES_SCORE
        if roles_count2 > 1:
            result['multiple_roles_score'] += self.MULTIPLE_ROLES_SCORE
        
        # Check appointment and resignation timing
        for company in shared_companies:
            roles1_company = [r for r in roles1 if r['company_number'] == company]
            roles2_company = [r for r in roles2 if r['company_number'] == company]
            
            for role1 in roles1_company:
                for role2 in roles2_company:
                    # Check appointment timing
                    if 'appointed_on' in role1 and 'appointed_on' in role2:
                        try:
                            date1 = datetime.strptime(role1['appointed_on'], '%Y-%m-%d')
                            date2 = datetime.strptime(role2['appointed_on'], '%Y-%m-%d')
                            if abs((date1 - date2).days) <= self.APPOINTMENT_TIMING_THRESHOLD:
                                result['timing_score'] += self.APPOINTMENT_TIMING_SCORE
                                break
                        except ValueError:
                            pass
                    
                    # Check resignation timing
                    if 'resigned_on' in role1 and 'resigned_on' in role2:
                        try:
                            date1 = datetime.strptime(role1['resigned_on'], '%Y-%m-%d')
                            date2 = datetime.strptime(role2['resigned_on'], '%Y-%m-%d')
                            if abs((date1 - date2).days) <= self.APPOINTMENT_TIMING_THRESHOLD:
                                result['timing_score'] += self.RESIGNATION_TIMING_SCORE
                                break
                        except ValueError:
                            pass
            
        return result
    
    def _check_psc_overlap(self, psc1: List[Dict], psc2: List[Dict]) -> int:
        """
        Calculate score based on shared ownership in companies.
        
        Args:
            psc1: PSC holdings for first person
            psc2: PSC holdings for second person
            
        Returns:
            Score based on overlapping PSCs
        """
        if not psc1 or not psc2:
            return 0
        
        # Convert to sets of company numbers
        companies1 = set(holding['company_number'] for holding in psc1)
        companies2 = set(holding['company_number'] for holding in psc2)
        
        shared_companies = companies1.intersection(companies2)
        
        score = len(shared_companies) * 20  # 20 points per shared ownership
        return min(score, 60)  # Cap at 60 points
    
    def _check_address_proximity(self, address1: Dict, address2: Dict) -> Dict:
        """
        Enhanced address checking that handles both exact matches and proximity.
        
        Args:
            address1: Address information for first person
            address2: Address information for second person
            
        Returns:
            Dictionary with exact match score and proximity score
        """
        result = {
            'exact_match_score': 0,
            'proximity_score': 0
        }
        
        if not address1 or not address2:
            return result
            
        # Check for exact address match first
        if address1.get('full_address') and address2.get('full_address'):
            if self._normalize_address(address1['full_address']) == self._normalize_address(address2['full_address']):
                result['exact_match_score'] = self.SHARED_ADDRESS_SCORE
                return result
        
        # If no exact match and geocoding is available, check proximity
        try:
            if all(key in address1 and key in address2 for key in ['latitude', 'longitude']):
                coord1 = (address1['latitude'], address1['longitude'])
                coord2 = (address2['latitude'], address2['longitude'])
                
                distance = geodesic(coord1, coord2).miles
                
                if distance <= self.ADDRESS_PROXIMITY_THRESHOLD:
                    result['proximity_score'] = self.NEARBY_ADDRESS_SCORE
            
        except (KeyError, TypeError, AttributeError):
            pass
            
        return result
        
    def _normalize_address(self, address: str) -> str:
        """
        Normalize address string for comparison by removing common variations.
        
        Args:
            address: Address string to normalize
            
        Returns:
            Normalized address string
        """
        if not address:
            return ""
            
        normalized = address.lower().strip()
        # Remove common variations like 'road/rd', 'street/st', etc.
        replacements = {
            ' road': ' rd',
            ' street': ' st',
            ' avenue': ' ave',
            ' lane': ' ln',
            ' close': ' cl',
            ' court': ' ct',
            ' drive': ' dr'
        }
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        return normalized
    
    def _check_surname_in_company_name(self, surname: str, company_name: str) -> int:
        """
        Check if person's surname appears in the company name.
        
        Args:
            surname: Person's surname
            company_name: Company name to check
            
        Returns:
            Score if surname found in company name, 0 otherwise
        """
        if not surname or not company_name:
            return 0
            
        surname = surname.lower().strip()
        company_name = company_name.lower().strip()
        
        # Use fuzzy matching to handle slight variations
        if fuzz.partial_ratio(surname, company_name) >= self.SURNAME_SIMILARITY_THRESHOLD:
            return self.COMPANY_NAME_SCORE
            
        return 0
    
    def _determine_confidence(self, total_score: float) -> str:
        """
        Determine confidence level based on total score.
        
        Args:
            total_score: Total connection score
            
        Returns:
            Confidence level string (LOW, MEDIUM, HIGH)
        """
        if total_score >= 150:
            return 'HIGH'
        elif total_score >= 100:
            return 'MEDIUM'
        else:
            return 'LOW'

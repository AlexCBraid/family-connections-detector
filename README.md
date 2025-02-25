# Family Connections Detector

A Python package for detecting potential family connections between corporate officers and directors using various indicators such as:

- Name similarity (surnames and middle names)
- Age relationships (siblings and parent-child patterns)
- Shared appointments
- Synchronized appointment/resignation timing
- Address proximity
- Company name matching

## Installation

```bash
# From GitHub
pip install git+https://github.com/yourusername/family_connections.git

# For development
git clone https://github.com/yourusername/family_connections.git
cd family_connections
pip install -e .
```

## Quick Start

```python
from family_connections import FamilyConnectionDetector

# Initialize the detector
detector = FamilyConnectionDetector()

# Example data
person1 = {
    'full_name': 'John Kennedy Smith',
    'middle_names': ['Kennedy'],
    'date_of_birth': '1980-05-15',
    'roles': [
        {
            'company_number': '12345678',
            'role_type': 'Director',
            'appointed_on': '2020-01-01'
        }
    ],
    'address': {
        'full_address': '123 Business St, London',
        'latitude': 51.5074,
        'longitude': -0.1278
    }
}

person2 = {
    # ... similar structure
}

# Calculate connection score
result = detector.calculate_connection_score(person1, person2)
print(f"Total Score: {result['total_score']}")
print(f"Confidence: {result['confidence']}")
for reason in result['reasons']:
    print(f"- {reason}")
```

## Features

- **Name Matching**: Detects similar surnames and shared middle names
- **Age Analysis**: Identifies potential sibling and parent-child relationships
- **Appointment Analysis**: 
  - Detects shared company appointments
  - Identifies synchronized appointment/resignation timing
  - Tracks multiple role holdings
- **Address Analysis**:
  - Exact address matching
  - Proximity-based matching using geocoding
- **Company Name Matching**: Identifies family surnames in company names

## Configuration

You can customize the scoring thresholds and weights by passing parameters to the `FamilyConnectionDetector` constructor:

```python
detector = FamilyConnectionDetector(
    surname_similarity_threshold=85,
    sibling_age_range=3,
    generational_age_gap=30,
    # ... other parameters
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# WorkoutBuddy Unit System Documentation (2024)

## Overview

WorkoutBuddy supports both metric and imperial units across all models and flows, including new tables for safety, privacy, ML feedback, accountability, and community. All downstream algorithms and ML models use metric units internally for consistency and accuracy.

## Architecture

### Database Schema

The database has been updated to support dual units with the following changes:

#### New Enums
- `unit_system`: `METRIC` or `IMPERIAL`
- `weight_unit`: `KG` or `LBS`
- `height_unit`: `CM`, `INCHES`, or `FEET_INCHES`
- `distance_unit`: `KM`, `MILES`, or `METERS`

#### Updated Tables

1. **users table**
   - Added `unit_system`, `height_unit`, `weight_unit` columns
   - `height` and `weight` are stored in user's preferred units

2. **user_stats table**
   - Added `weight_unit`, `distance_unit` columns
   - All measurements stored with their original units

3. **workout_exercises table**
   - Added `weight_unit`, `distance_unit` columns
   - Weight and distance stored in user's preferred units

#### Metric Views

For algorithms, metric views are created that automatically convert all measurements to metric units:

- `users_metric`: Users with height in cm and weight in kg
- `user_stats_metric`: User stats with weight in kg and distance in km
- `workout_exercises_metric`: Workout exercises with weight in kg and distance in meters

#### Conversion Functions

PostgreSQL functions for unit conversions:
- `lbs_to_kg(lbs)`, `kg_to_lbs(kg)`
- `inches_to_cm(inches)`, `cm_to_inches(cm)`
- `miles_to_km(miles)`, `km_to_miles(km)`

## Model Implementation

### User Model

```python
class User(Base):
    # Unit preferences
    unit_system = Column(Enum(UnitSystem), default=UnitSystem.METRIC)
    height_unit = Column(Enum(HeightUnit), default=HeightUnit.CM)
    weight_unit = Column(Enum(WeightUnit), default=WeightUnit.KG)

    # Measurements stored in user's preferred units
    height = Column(Float)  # stored in height_unit
    weight = Column(Float)  # stored in weight_unit

    def get_height_cm(self) -> float:
        """Get height in centimeters (metric)"""
        # Converts from user's unit to cm

    def get_weight_kg(self) -> float:
        """Get weight in kilograms (metric)"""
        # Converts from user's unit to kg
```

### UserStats Model

```python
class UserStats(Base):
    # Unit tracking
    weight_unit = Column(Enum(WeightUnit), default=WeightUnit.KG)
    distance_unit = Column(Enum(DistanceUnit), default=DistanceUnit.KM)

    # Measurements stored in original units
    weight = Column(Float)  # stored in weight_unit
    muscle_mass = Column(Float)  # stored in weight_unit
    total_weight_lifted = Column(Float)  # stored in weight_unit
    total_cardio_distance = Column(Float)  # stored in distance_unit

    def get_weight_kg(self) -> float:
        """Get weight in kilograms (metric)"""

    def get_total_weight_lifted_kg(self) -> float:
        """Get total weight lifted in kilograms (metric)"""
```

### WorkoutExercise Model

```python
class WorkoutExercise(Base):
    # Unit tracking
    weight_unit = Column(Enum(WeightUnit), default=WeightUnit.KG)
    distance_unit = Column(Enum(DistanceUnit), default=DistanceUnit.METERS)

    # Measurements stored in user's preferred units
    weight = Column(String)  # stored in weight_unit (can be "60,65,70")
    distance = Column(Float)  # stored in distance_unit
    speed = Column(Float)  # stored in distance_unit per hour

    def get_weight_kg(self) -> str:
        """Get weight in kilograms (metric)"""

    def get_distance_meters(self) -> float:
        """Get distance in meters (metric)"""
```

## Unit Conversion Utilities

### UnitConverter Class

```python
class UnitConverter:
    # Conversion constants
    LBS_TO_KG = 0.45359237
    KG_TO_LBS = 2.20462262
    INCHES_TO_CM = 2.54
    CM_TO_INCHES = 1 / 2.54
    MILES_TO_KM = 1.609344
    KM_TO_MILES = 1 / 1.609344

    @staticmethod
    def lbs_to_kg(lbs: float) -> float:
        """Convert pounds to kilograms"""

    @staticmethod
    def kg_to_lbs(kg: float) -> float:
        """Convert kilograms to pounds"""

    @staticmethod
    def convert_weight_string(weight_str: str, from_unit: str, to_unit: str) -> str:
        """Convert weight string from one unit to another"""

    @staticmethod
    def format_height_display(height_cm: float, unit: str) -> str:
        """Format height for display in specified unit"""
```

### UnitPreferences Class

```python
class UnitPreferences:
    def __init__(self, unit_system: str = "METRIC", height_unit: str = "CM", weight_unit: str = "KG"):
        self.unit_system = unit_system
        self.height_unit = height_unit
        self.weight_unit = weight_unit

    def convert_for_display(self, value: float, measurement_type: str) -> float:
        """Convert a metric value to the user's preferred unit for display"""

    def convert_from_display(self, value: float, measurement_type: str) -> float:
        """Convert a value from user's preferred unit to metric"""
```

## ML Service Integration

### Metric Models

All ML models use metric units internally:

```python
@dataclass
class User:
    height_cm: Optional[float] = None  # Always in centimeters
    weight_kg: Optional[float] = None  # Always in kilograms
    unit_system: Optional[str] = "METRIC"
    height_unit: Optional[str] = "CM"
    weight_unit: Optional[str] = "KG"
```

### Algorithm Usage

ML algorithms use metric views for consistent data:

```python
class UserSimilarityModel:
    def extract_user_features(self, user: User, db: Session) -> np.ndarray:
        # Use metric conversion methods
        height_cm = user.get_height_cm() if hasattr(user, 'get_height_cm') else user.height_cm
        weight_kg = user.get_weight_kg() if hasattr(user, 'get_weight_kg') else user.weight_kg

        # Use metric views for workout data
        result = db.execute(text("""
            SELECT COALESCE(SUM(total_weight_lifted_kg), 0) as total_weight
            FROM user_stats_metric
            WHERE user_id = :user_id
        """))
```

## API Schemas

### User Schemas

```python
class UserUpdate(BaseModel):
    height: Optional[float] = Field(None, gt=0)  # In user's preferred height_unit
    weight: Optional[float] = Field(None, gt=0)  # In user's preferred weight_unit
    unit_system: Optional[str] = Field(None, regex="^(METRIC|IMPERIAL)$")
    height_unit: Optional[str] = Field(None, regex="^(CM|INCHES|FEET_INCHES)$")
    weight_unit: Optional[str] = Field(None, regex="^(KG|LBS)$")

    @validator('height')
    def validate_height(cls, v, values):
        """Validate height based on unit"""

class UserMetricResponse(BaseModel):
    height_cm: Optional[float] = None  # Always in centimeters
    weight_kg: Optional[float] = None  # Always in kilograms
```

### Workout Schemas

```python
class WorkoutExerciseBase(BaseModel):
    weight: Optional[str] = None  # Stored in user's preferred weight_unit
    distance: Optional[float] = None  # Stored in user's preferred distance_unit
    weight_unit: Optional[str] = Field(None, regex="^(KG|LBS)$")
    distance_unit: Optional[str] = Field(None, regex="^(KM|MILES|METERS)$")

    @validator('weight')
    def validate_weight(cls, v, values):
        """Validate weight based on unit"""

class WorkoutExerciseMetricResponse(BaseModel):
    weight_kg: Optional[str] = None  # Always in kilograms
    distance_meters: Optional[float] = None  # Always in meters
```

## Usage Patterns

### Frontend Display

```python
# Convert metric values to user's preferred units for display
user_prefs = UnitPreferences(
    unit_system=user.unit_system,
    height_unit=user.height_unit,
    weight_unit=user.weight_unit
)

# Display height
height_display = user_prefs.convert_for_display(user.get_height_cm(), "height")
height_formatted = UnitConverter.format_height_display(user.get_height_cm(), user.height_unit)

# Display weight
weight_display = user_prefs.convert_for_display(user.get_weight_kg(), "weight")
weight_formatted = UnitConverter.format_weight_display(user.get_weight_kg(), user.weight_unit)
```

### Backend Processing

```python
# Store user input in their preferred units
user_input_height = 70  # inches
user_input_weight = 150  # lbs

# Convert to metric for algorithms
height_cm = UnitConverter.inches_to_cm(user_input_height)
weight_kg = UnitConverter.lbs_to_kg(user_input_weight)

# Store in user's preferred units
user.height = user_input_height
user.weight = user_input_weight
user.height_unit = "INCHES"
user.weight_unit = "LBS"
```

### ML Algorithm Input

```python
# Always use metric units for algorithms
user_features = [
    user.get_height_cm(),  # Always in cm
    user.get_weight_kg(),  # Always in kg
    # ... other features
]

# Use metric views for workout data
result = db.execute(text("""
    SELECT weight_kg, distance_meters
    FROM workout_exercises_metric
    WHERE user_id = :user_id
"""))
```

## Testing

### Unit Tests

All tests use metric units internally:

```python
def test_extract_user_features_imperial_conversion(self):
    """Test feature extraction with imperial to metric conversion"""
    user = User(
        height_cm=175.0,  # Will be converted from inches
        weight_kg=70.0,   # Will be converted from lbs
        unit_system="IMPERIAL",
        height_unit="INCHES",
        weight_unit="LBS",
    )

    # Mock conversion methods
    user.get_height_cm = lambda: 175.0  # Converted from inches
    user.get_weight_kg = lambda: 70.0   # Converted from lbs
```

## Migration Guide

### Database Migration

Run the schema update script:

```bash
python scripts/update_schema_units.py
```

This will:
1. Create unit enums
2. Add unit columns to tables
3. Create conversion functions
4. Create metric views

### Code Updates

1. **Update models** to include unit fields and conversion methods
2. **Update schemas** to support unit validation
3. **Update ML models** to use metric units
4. **Update tests** to use metric units internally
5. **Update API endpoints** to handle unit preferences

### Frontend Updates

1. **Add unit preference settings** to user profile
2. **Update forms** to include unit selection
3. **Add unit conversion** for display
4. **Update validation** to check unit-specific ranges

## Benefits

1. **User Experience**: Users can work in their preferred units
2. **Algorithm Consistency**: All ML algorithms use metric units
3. **Data Integrity**: Original units are preserved
4. **Flexibility**: Easy to add new units or conversion factors
5. **Performance**: Metric views provide fast access to converted data

## Best Practices

1. **Always use metric units** in algorithms and calculations
2. **Store original units** with measurements
3. **Convert at boundaries** (UI ↔ API ↔ Database)
4. **Validate unit ranges** based on the unit type
5. **Use metric views** for algorithm data access
6. **Test both unit systems** thoroughly
7. **Document unit assumptions** in code comments

## Future Enhancements

1. **Additional units**: Support for stone, yards, etc.
2. **Automatic unit detection**: Based on user location
3. **Unit conversion caching**: For performance
4. **Custom unit preferences**: Per measurement type
5. **Unit conversion history**: Track changes over time

## Test Coverage

- All unit system features are covered by integration and synthetic data tests.
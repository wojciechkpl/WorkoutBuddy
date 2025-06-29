"""
Unit conversion utilities for WorkoutBuddy

This module provides conversion functions between metric and imperial units.
All algorithms should use metric units internally, while the UI can display
in the user's preferred units.
"""


class UnitConverter:
    """Utility class for unit conversions"""

    # Conversion constants
    LBS_TO_KG = 0.45359237
    KG_TO_LBS = 2.20462262
    INCHES_TO_CM = 2.54
    CM_TO_INCHES = 1 / 2.54
    MILES_TO_KM = 1.609344
    KM_TO_MILES = 1 / 1.609344
    FEET_TO_INCHES = 12

    @staticmethod
    def lbs_to_kg(lbs: float) -> float:
        """Convert pounds to kilograms"""
        return lbs * UnitConverter.LBS_TO_KG

    @staticmethod
    def kg_to_lbs(kg: float) -> float:
        """Convert kilograms to pounds"""
        return kg * UnitConverter.KG_TO_LBS

    @staticmethod
    def inches_to_cm(inches: float) -> float:
        """Convert inches to centimeters"""
        return inches * UnitConverter.INCHES_TO_CM

    @staticmethod
    def cm_to_inches(cm: float) -> float:
        """Convert centimeters to inches"""
        return cm * UnitConverter.CM_TO_INCHES

    @staticmethod
    def miles_to_km(miles: float) -> float:
        """Convert miles to kilometers"""
        return miles * UnitConverter.MILES_TO_KM

    @staticmethod
    def km_to_miles(km: float) -> float:
        """Convert kilometers to miles"""
        return km * UnitConverter.KM_TO_MILES

    @staticmethod
    def feet_inches_to_cm(feet: int, inches: int) -> float:
        """Convert feet and inches to centimeters"""
        total_inches = (feet * UnitConverter.FEET_TO_INCHES) + inches
        return total_inches * UnitConverter.INCHES_TO_CM

    @staticmethod
    def cm_to_feet_inches(cm: float) -> tuple[int, int]:
        """Convert centimeters to feet and inches"""
        total_inches = cm * UnitConverter.CM_TO_INCHES
        feet = int(total_inches // UnitConverter.FEET_TO_INCHES)
        inches = int(total_inches % UnitConverter.FEET_TO_INCHES)
        return feet, inches

    @staticmethod
    def parse_weight_string(weight_str: str) -> list[float]:
        """Parse weight string (e.g., '60,65,70' or '100') into list of floats"""
        if not weight_str:
            return []

        try:
            return [float(w.strip()) for w in weight_str.split(",")]
        except (ValueError, AttributeError):
            return []

    @staticmethod
    def format_weight_string(weights: list[float], precision: int = 2) -> str:
        """Format list of weights into string (e.g., [60.0, 65.0, 70.0] -> '60.00,65.00,70.00')"""
        if not weights:
            return ""

        return ",".join([f"{w:.{precision}f}" for w in weights])

    @staticmethod
    def convert_weight_string(weight_str: str, from_unit: str, to_unit: str) -> str:
        """Convert weight string from one unit to another"""
        if from_unit == to_unit:
            return weight_str

        weights = UnitConverter.parse_weight_string(weight_str)
        if not weights:
            return weight_str

        if from_unit == "LBS" and to_unit == "KG":
            converted_weights = [UnitConverter.lbs_to_kg(w) for w in weights]
        elif from_unit == "KG" and to_unit == "LBS":
            converted_weights = [UnitConverter.kg_to_lbs(w) for w in weights]
        else:
            return weight_str

        return UnitConverter.format_weight_string(converted_weights)

    @staticmethod
    def format_height_display(height_cm: float, unit: str) -> str:
        """Format height for display in specified unit"""
        if height_cm is None:
            return "N/A"

        if unit == "CM":
            return f"{height_cm:.1f} cm"
        elif unit == "INCHES":
            inches = UnitConverter.cm_to_inches(height_cm)
            return f"{inches:.1f} inches"
        elif unit == "FEET_INCHES":
            feet, inches = UnitConverter.cm_to_feet_inches(height_cm)
            return f"{feet}' {inches}\""
        else:
            return f"{height_cm:.1f} cm"

    @staticmethod
    def format_weight_display(weight_kg: float, unit: str) -> str:
        """Format weight for display in specified unit"""
        if weight_kg is None:
            return "N/A"

        if unit == "KG":
            return f"{weight_kg:.1f} kg"
        elif unit == "LBS":
            lbs = UnitConverter.kg_to_lbs(weight_kg)
            return f"{lbs:.1f} lbs"
        else:
            return f"{weight_kg:.1f} kg"

    @staticmethod
    def format_distance_display(distance_km: float, unit: str) -> str:
        """Format distance for display in specified unit"""
        if distance_km is None:
            return "N/A"

        if unit == "KM":
            return f"{distance_km:.2f} km"
        elif unit == "MILES":
            miles = UnitConverter.km_to_miles(distance_km)
            return f"{miles:.2f} miles"
        elif unit == "METERS":
            meters = distance_km * 1000
            return f"{meters:.0f} m"
        else:
            return f"{distance_km:.2f} km"


class UnitPreferences:
    """Helper class for managing user unit preferences"""

    def __init__(
        self,
        unit_system: str = "METRIC",
        height_unit: str = "CM",
        weight_unit: str = "KG",
    ):
        self.unit_system = unit_system
        self.height_unit = height_unit
        self.weight_unit = weight_unit

    def get_display_unit(self, measurement_type: str) -> str:
        """Get the display unit for a given measurement type"""
        if measurement_type == "height":
            return self.height_unit
        elif measurement_type == "weight":
            return self.weight_unit
        elif measurement_type == "distance":
            return "KM" if self.unit_system == "METRIC" else "MILES"
        else:
            return "CM" if self.unit_system == "METRIC" else "INCHES"

    def convert_for_display(self, value: float, measurement_type: str) -> float:
        """Convert a metric value to the user's preferred unit for display"""
        if value is None:
            return None

        if measurement_type == "height":
            if self.height_unit == "CM":
                return value
            elif self.height_unit == "INCHES":
                return UnitConverter.cm_to_inches(value)
            elif self.height_unit == "FEET_INCHES":
                return UnitConverter.cm_to_inches(value)  # Return total inches

        elif measurement_type == "weight":
            if self.weight_unit == "KG":
                return value
            elif self.weight_unit == "LBS":
                return UnitConverter.kg_to_lbs(value)

        elif measurement_type == "distance":
            if self.unit_system == "METRIC":
                return value
            else:
                return UnitConverter.km_to_miles(value)

        return value

    def convert_from_display(self, value: float, measurement_type: str) -> float:
        """Convert a value from user's preferred unit to metric"""
        if value is None:
            return None

        if measurement_type == "height":
            if self.height_unit == "CM":
                return value
            elif self.height_unit == "INCHES":
                return UnitConverter.inches_to_cm(value)
            elif self.height_unit == "FEET_INCHES":
                return UnitConverter.inches_to_cm(value)  # Value is total inches

        elif measurement_type == "weight":
            if self.weight_unit == "KG":
                return value
            elif self.weight_unit == "LBS":
                return UnitConverter.lbs_to_kg(value)

        elif measurement_type == "distance":
            if self.unit_system == "METRIC":
                return value
            else:
                return UnitConverter.miles_to_km(value)

        return value


# Convenience functions for common conversions
def lbs_to_kg(lbs: float) -> float:
    """Convert pounds to kilograms"""
    return UnitConverter.lbs_to_kg(lbs)


def kg_to_lbs(kg: float) -> float:
    """Convert kilograms to pounds"""
    return UnitConverter.kg_to_lbs(kg)


def inches_to_cm(inches: float) -> float:
    """Convert inches to centimeters"""
    return UnitConverter.inches_to_cm(inches)


def cm_to_inches(cm: float) -> float:
    """Convert centimeters to inches"""
    return UnitConverter.cm_to_inches(cm)


def miles_to_km(miles: float) -> float:
    """Convert miles to kilometers"""
    return UnitConverter.miles_to_km(miles)


def km_to_miles(km: float) -> float:
    """Convert kilometers to miles"""
    return UnitConverter.km_to_miles(km)

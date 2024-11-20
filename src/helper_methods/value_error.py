"""
    Functions i.e Value Errors
    and Exceptions to avoid 
    redundency of Code

"""


def validate_time_slot(time_slot):
        """Helper method to validate time slot."""
        if time_slot < 0 or time_slot >= 7:
            raise ValueError("Time Slot Out of Range")
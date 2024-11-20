from helper_methods.value_error import validate_time_slot

class room:
    def __init__(self, room_name):
        self.room_name = room_name
        self.availability = {}

    def add_availability(self, time_slot, is_available):
        validate_time_slot(time_slot)
        self.availability[time_slot] = is_available
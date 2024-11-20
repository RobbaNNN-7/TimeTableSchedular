from helper_methods.value_error import validate_time_slot

class Room:
    def __init__(self, room_id, capacity, availability):
        self.room_id = room_id
        self.capacity = capacity
        self.availability = [True] * 7  # Mark all Slots as True

    def is_available(self, time_slot):
        validate_time_slot(time_slot)  
        return self.availability[time_slot]

    def assign_course(self, time_slot):
        validate_time_slot(time_slot)  
        self.availability[time_slot] = False

    def remove_course(self, time_slot):
        validate_time_slot(time_slot)
        self.availability[time_slot] = True

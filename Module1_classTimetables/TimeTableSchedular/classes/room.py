class Room:
    def __init__(self, room_name):
        self.room_name = room_name
        self.availability = {}

    def add_availability(self, time_slot, is_available):
        if not (0 <= time_slot < 7):
            raise ValueError("Time Slot Out of Range")
        self.availability[time_slot] = is_available
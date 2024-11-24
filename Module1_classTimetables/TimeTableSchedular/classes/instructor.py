class Instructor:
    def __init__(self, id):
        self.id = id
        self.availability = [True] * 7
        
    def is_available(self, time_slot):
        if not (0 <= time_slot < 7):
            raise ValueError("Time Slot Out of Range")
        return self.availability[time_slot]

    def assign_course(self, time_slot):
        if not (0 <= time_slot < 7):
            raise ValueError("Time Slot Out of Range")
        self.availability[time_slot] = False

    def remove_course(self, time_slot):
        if not (0 <= time_slot < 7):
            raise ValueError("Time Slot Out of Range")
        self.availability[time_slot] = True
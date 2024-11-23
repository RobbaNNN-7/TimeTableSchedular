class Course:
    def __init__(self, name, course_type=None, credits=None):
        self.name = name
        self.type = course_type
        self.credits = credits
        self.instructor = []
        self.room = []
        self.time_slot = []
        self.possible_time_slots = []
        self.possible_rooms = []
        self.possible_instructors = []

    def add_possible_time_slot(self, time_slot):
        if not (0 <= time_slot < 7):
            raise ValueError("Time Slot Out of Range")
        self.possible_time_slots.append(time_slot)

    def add_possible_room(self, room):
        self.possible_rooms.append(room)

    def add_possible_instructor(self, instructor):
        self.possible_instructors.append(instructor)
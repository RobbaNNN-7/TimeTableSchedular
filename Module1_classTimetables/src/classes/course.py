import instructor,room

class course:
    def __init__(self,name,instructor,duration,room,time_slot,type,id,credits):
        self.name = name
        self.instructor = instructor
        self.type  = type
        self.id = id
        self.credits = credits
        self.room = None
        self.time_slot = None

    def assign_room(self,room,time_slot):
        if room.is_availible() and instructor.is_availible():
            self.room = room
            room.assign_course(time_slot) # Marks a slot as False 
            self.time_slot = time_slot
            return True # Success
        
        return False
    
    def assign_instructor(self,time_slot):
        if instructor.is_availible():
            self.instructor.assign_course(time_slot)
            return True # Success
        return False

    def display_course_info(self):
        print(self.name)
        print(self.type)
        print(self.id)
        print(self.instructor)
        print(self.credits)

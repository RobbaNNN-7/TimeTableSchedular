from Module1_classTimetables.src.helper_methods.value_error import *
import instructor,room
from 

class course:
    def __init__(self,name,instructor,duration,room,time_slot,type,id,credits):
        self.name = name
        self.type  = type
        self.credits = credits
        self.instructor = []
        self.room = []
        self.time_slot = []

    
    def add_possible_time_slot(self, time_slot):
        validate_time_slot(time_slot)
        self.possible_time_slots.append(time_slot)

    def add_possible_room(self, room):
        validate_room_no(room)
        self.possible_rooms.append(room)

    def add_possible_instructor(self, instructor):
        validate_instructor(instructor)
        self.possible_instructors.append(instructor)

    
    # def assign_room(self,room,time_slot):
    #     if room.is_availible() and instructor.is_availible():
    #         self.room = room
    #         room.assign_course(time_slot) # Marks a slot as False 
    #         self.time_slot = time_slot
    #         return True # Success
        
    #     return False
    
    # def assign_instructor(self,time_slot):
    #     if instructor.is_availible():
    #         self.instructor.assign_course(time_slot)
    #         return True # Success
    #     return False

    # def display_course_info(self):
    #     print(self.name)
    #     print(self.type)
    #     print(self.id)
    #     print(self.instructor)
    #     print(self.credits)

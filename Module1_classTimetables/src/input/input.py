
from Module1_classTimetables.src.classes import course, instructor,room,sections
from Module1_classTimetables.src.global_variables import *

""" Hard Coded Inputs

Include:
        Courses
        TimeSlots
        Instructors
        Rooms
        Sections
"""



courses = [

    course('Math 101'),
    course('Physics 101'),
    course('Chemistry 101'),
    course('Biology 101'),
    course('CS 101'),
    course('History 101')
    
]

time_slots = [
    "9:00 AM",
    "10:00 AM",
    "11:00 AM", 
    "12:00 PM", 
    "2:00 PM", 
    "3:00 PM",
    "4:00 PM"
]

rooms = [room(i) for i in range(1,TOTAL_ROOMS)]

sections = []
for i in range(1, TOTAL_SECTIONS):
    section = Section(f"Section {i}", courses)
    sections.append(section)


instructors = [instructor(f"Instructor {i}") for i in range(1, TOTAL_INSTRUCTORS)]




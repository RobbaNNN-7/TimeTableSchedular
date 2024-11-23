from classes.course import Course
from classes.room import Room
from classes.instructor import Instructor
from classes.section import Section
from global_variables import TOTAL_ROOMS, TOTAL_INSTRUCTORS, TOTAL_SECTIONS
# Course definitions
COURSES = [
    Course('Math 101'),
    Course('Physics 101'),
    Course('Chemistry 101'),
    Course('Biology 101'),
    Course('CS 101'),
    Course('History 101')
]

# Time slot definitions
TIME_SLOTS = [
    "9:00 AM",
    "10:00 AM",
    "11:00 AM", 
    "12:00 PM", 
    "2:00 PM", 
    "3:00 PM",
    "4:00 PM"
]

# Generate rooms, instructors, and sections
ROOMS = [Room(f"Room {i}") for i in range(1, TOTAL_ROOMS)]
INSTRUCTORS = [Instructor(f"Instructor {i}") for i in range(1, TOTAL_INSTRUCTORS)]
SECTIONS = [Section(f"Section {i}", COURSES) for i in range(1, TOTAL_SECTIONS)]
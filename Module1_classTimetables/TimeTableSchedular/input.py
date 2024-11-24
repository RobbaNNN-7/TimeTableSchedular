from classes.course import Course
from classes.room import Room
from classes.instructor import Instructor
from classes.section import Section
from global_variables import TOTAL_ROOMS, TOTAL_INSTRUCTORS, TOTAL_SECTIONS
# Course definitions
COURSES = [
    Course(name='Programming Fundamentals', credits=3),
    Course(name='Digital Logic Design', credits=3),
    Course(name='Discrete Structures', credits=3),
    Course(name='Physics Lab', credits=1),
    Course(name='Communication & Presentation Skills', credits=2)
]

# Time slot definitions matching your format
TIME_SLOTS = [
    '0900-0950',
    '1000-1050',
    '1100-1150',
    '1200-1250',
    '1400-1450',
    '1500-1550',
    '1600-1650'
]

# Generate rooms with meaningful names
ROOMS = [
    Room("CS-1"),
    Room("CS-2"),
    Room("CS-3"),
    Room("LAB-1"),
    Room("LAB-2")
]

# Generate instructors
INSTRUCTORS = [
    Instructor("INS-1"),
    Instructor("INS-2"),
    Instructor("INS-3"),
    Instructor("INS-4"),
    Instructor("INS-5")
]

# Modified Section creation
def create_sections():
    section_numbers = ['13', '14', '15', '16', '17']
    sections = []
    
    for section_num in section_numbers:
        for course in COURSES:
            # Create a unique section name that includes both section number and course
            section_name = f"Section {section_num}"
            sections.append(Section(section_name, course))
    
    return sections

SECTIONS = create_sections()
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Optional
from classes.Student import *
from classes.Classroom import *
from Csp import *


# Example usage of CSP for exam seating arrangement

# Create some students
students = [
    Student("S1", "CS", "A", "Math"),
    Student("S2", "EE", "B", "Physics"),
    Student("S3", "DS", "C", "Chemistry"),
    Student("S4", "CS", "A", "Math"),
    Student("S5", "EE", "B", "Physics"),
    Student("S6", "DS", "C", "Chemistry"),
    Student("S7", "CS", "A", "Math"),
    Student("S8", "EE", "B", "Physics"),
    Student("S9", "DS", "C", "Chemistry"),
    Student("S10", "CS", "A", "Math"),
    Student("S11", "EE", "B", "Physics"),
    Student("S12", "DS", "C", "Chemistry")
]

# Create some classrooms
classrooms = [
    Classroom("Room1", 2, 3),  # 2 columns, 3 seats per column
    Classroom("Room2", 2, 3),
]

# Initialize CSP
csp = CSP(students, classrooms)

# Solve the CSP problem
solution = csp.solve()

# Print the solution
if solution:
    for (classroom, col, row), student in solution.items():
        print(f"Classroom: {classroom}, Seat: ({col}, {row}), Student: {student.student_id}, Subject: {student.subject}")
else:
    print("No solution found")
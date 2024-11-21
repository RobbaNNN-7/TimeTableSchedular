from collections import defaultdict, deque
from typing import List, Dict, Tuple, Optional
from classes.Student import *
from classes.Classroom import *
from classes.Exam import *
from Csp import *



# Example Usage
students = [
    Student("S1", "CS", "A"),
    Student("S2", "CS", "A"),
    Student("S3", "CS", "B"),
    Student("S4", "ECE", "A"),
    Student("S5", "ECE", "B"),
]

classrooms = [
    Classroom("Room1", 2, 3),
    Classroom("Room2", 3, 4),
]

exams = [
    Exam("CS", "Math"),
    Exam("ECE", "Physics"),
]

csp = CSP(students, classrooms, exams)
solution = csp.solve()

if solution:
    for var, student in solution.items():
        print(f"Seat {var} -> {student.student_id if student else 'Empty'}")
else:
    print("No solution found.")

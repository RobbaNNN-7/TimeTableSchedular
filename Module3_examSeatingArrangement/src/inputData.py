from collections import defaultdict
from typing import List, Dict, Tuple


class Student:
    def __init__(self, student_id: str, department: str, section: str):
        self.student_id = student_id
        self.department = department
        self.section = section


class Classroom:
    def __init__(self, name: str, num_columns: int, seats_per_column: int):
        self.name = name
        self.num_columns = num_columns
        self.seats_per_column = seats_per_column
        self.seating = [["" for _ in range(num_columns)] for _ in range(seats_per_column)]


class Exam:
    def __init__(self, department: str, subject: str):
        self.department = department
        self.subject = subject


def arrange_seating(students: List[Student], classrooms: List[Classroom], exams: List[Exam]) -> Dict[str, List[List[str]]]:
    # Group students by department and section
    grouped_students = defaultdict(lambda: defaultdict(list))
    for student in students:
        grouped_students[student.department][student.section].append(student)

    # Assign students to classrooms and columns
    classroom_arrangements = {}
    assigned_students = set()

    for classroom in classrooms:
        seating = [[None for _ in range(classroom.num_columns)] for _ in range(classroom.seats_per_column)]
        current_col = 0
        current_row = 0

        for exam in exams:
            dept_students = grouped_students[exam.department]
            for section, section_students in dept_students.items():
                for student in section_students:
                    if student.student_id in assigned_students:
                        continue
                    # Place student in the current seat
                    seating[current_row][current_col] = student
                    assigned_students.add(student.student_id)

                    # Move to the next seat
                    current_row += 1
                    if current_row == classroom.seats_per_column:
                        current_row = 0
                        current_col += 1
                        if current_col == classroom.num_columns:
                            break  # Move to the next classroom
                if current_col == classroom.num_columns:
                    break
            if current_col == classroom.num_columns:
                break

        # Convert seating to output format
        classroom_seating = [
            [f"{seat.student_id} ({seat.department}-{seat.section})" if seat else "" for seat in row]
            for row in seating
        ]
        classroom_arrangements[classroom.name] = classroom_seating

    return classroom_arrangements


# Example Usage:
students = [
    Student("S1", "CS", "A"),
    Student("S2", "CS", "A"),
    Student("S3", "CS", "B"),
    Student("S4", "ECE", "A"),
    Student("S5", "ECE", "B"),
    Student("S6", "ECE", "B"),
    Student("S7", "ECE", "B"),
    Student("S8", "ECE", "A"),
    Student("S9", "CS", "B"),
    Student("S10", "CS", "A"),
    Student("S11", "CS", "A"),
    Student("S12", "CS", "B"),
    Student("S13", "ECE", "A"),
    Student("S14", "ECE", "B"),
    Student("S15", "ECE", "B"),
    Student("S16", "ECE", "B"),
    Student("S17", "ECE", "A"),
    Student("S18", "CS", "B"),
    Student("S19", "CS", "A"),
    Student("S20", "CS", "A"),
    Student("S21", "CS", "B"),
    Student("S22", "ECE", "A"),
    Student("S23", "ECE", "B"),
    Student("S24", "ECE", "B"),
    Student("S25", "ECE", "B"),
    Student("S26", "ECE", "A"),

]

classrooms = [
    Classroom("Room1", 3, 5),
    Classroom("Room2", 3, 5),
]

exams = [
    Exam("CS", "Math"),
    Exam("ECE", "Physics"),
]

arrangements = arrange_seating(students, classrooms, exams)

for room, seating in arrangements.items():
    print(f"Classroom: {room}")
    for row in seating:
        print(row)
    print()

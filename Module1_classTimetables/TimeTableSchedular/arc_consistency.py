import os
import sys

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(parent_dir)

from input import COURSES, TIME_SLOTS, ROOMS, INSTRUCTORS, SECTIONS



def arc_consistency(variables, domains, constraints):
    queue = [(X, Y) for X in variables for Y in variables if X != Y]
    
    while queue:
        X, Y = queue.pop(0)
        if revise(X, Y, domains, constraints):
            if not domains[X]:
                return False
                
            for Z in variables:
                if Z != X and (Z, X) in constraints:
                    queue.append((Z, X))
    return True

def revise(X, Y, domains, constraints):
    revised = False
    for value_x in list(domains[X]):  # Create a copy of the list to iterate
        if not any(is_consistent(value_x, value_y, constraints.get((X, Y))) 
                  for value_y in domains[Y]):
            domains[X].remove(value_x)
            revised = True
    return revised

def is_consistent(value_x, value_y, constraint):
    if constraint is None:
        return True
    return constraint(value_x, value_y)

def populate_timetable():
    variables = []
    domains = {}
    constraints = {}

    # Create variables and domains
    for section in SECTIONS:
        for course in COURSES:
            var = f"{course.name} ({section.section_name})"
            variables.append(var)
            
            domains[var] = [
                (time_slot, room, instructor) 
                for time_slot in TIME_SLOTS
                for room in ROOMS
                for instructor in INSTRUCTORS
            ]

    # Define constraints
    for X in variables:
        for Y in variables:
            if X != Y:
                constraints[(X, Y)] = lambda x, y: (
                    (x[0] != y[0] or x[1] != y[1]) and  # Same time-slot and room
                    (x[0] != y[0] or x[2] != y[2])      # Same time-slot and instructor
                )

    # Apply arc-consistency
    if not arc_consistency(variables, domains, constraints):
        print("No solution found (arc-consistency failed)")
        return None

    # Try to find a solution using backtracking
    assignment = {}
    if not backtrack(assignment, variables, domains, constraints):
        print("No valid timetable found (backtracking failed)")
        return None

    return assignment

def backtrack(assignment, variables, domains, constraints):
    if len(assignment) == len(variables):
        return True

    var = select_unassigned_variable(variables, assignment)
    for value in domains[var]:
        if is_assignment_consistent(var, value, assignment, constraints):
            assignment[var] = value
            if backtrack(assignment, variables, domains, constraints):
                return True
            assignment.pop(var)
    return False

def select_unassigned_variable(variables, assignment):
    return next(var for var in variables if var not in assignment)

def is_assignment_consistent(var, value, assignment, constraints):
    return all(
        is_consistent(value, assignment[assigned_var], constraints.get((var, assigned_var)))
        for assigned_var in assignment
    )

def display_timetable(assignment):
    if not assignment:
        print("No timetable to display")
        return

    timetable = {}
    for course_section, details in assignment.items():
        course, section = course_section.split(" (")
        section = section.strip(")")
        if section not in timetable:
            timetable[section] = []
        timetable[section].append((course, *details))

    for section, schedules in timetable.items():
        print(f"\nTimetable for {section}:")
        print("-" * 60)
        for course, time_slot, room, instructor in sorted(schedules, key=lambda x: TIME_SLOTS.index(x[1])):
            print(f"Course: {course:<15} Time: {time_slot:<10} Room: {room.room_name:<10} Instructor: {instructor.id}")
        print("-" * 60)

def main():
    timetable = populate_timetable()
    display_timetable(timetable)

if __name__ == "__main__":
    main()
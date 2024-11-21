from collections import defaultdict, deque
from typing import List, Dict, Tuple, Optional
from classes.Student import *
from classes.Classroom import *
from classes.Exam import *


class CSP:
    def __init__(self, students: List[Student], classrooms: List[Classroom], exams: List[Exam]):
        self.students = students
        self.classrooms = classrooms
        self.exams = exams
        self.variables = []  # List of all seats (variables)
        self.domains = {}  # Maps each variable to a list of possible students (domain)
        self.constraints = defaultdict(list)  # Maps a variable to its constraints
        self.assignments = {}  # Final assignment of students to seats

    def initialize(self):
        # Create variables for all seats in all classrooms
        self.variables = [
            (classroom.name, col, row)
            for classroom in self.classrooms
            for col in range(classroom.num_columns)
            for row in range(classroom.seats_per_column)
        ]

        # Initialize domains (all students for all seats initially)
        self.domains = {var: self.students[:] for var in self.variables}

        # Initialize constraints
        self.define_constraints()

    def define_constraints(self):
        """
        Define constraints between variables.
        """
        for classroom in self.classrooms:
            # Column-based constraints for the same classroom
            for col in range(classroom.num_columns):
                column_vars = [
                    (classroom.name, col, row) for row in range(classroom.seats_per_column)
                ]
                # No two students in the same column can have the same subject
                for var1 in column_vars:
                    for var2 in column_vars:
                        if var1 != var2:
                            self.constraints[var1].append(var2)  # Store related variables only

    def ac3(self):
        """
        Enforce arc-consistency using the AC-3 algorithm.
        """
        queue = deque((var1, var2) for var1 in self.variables for var2 in self.constraints[var1])

        while queue:
            var1, var2 = queue.popleft()
            if self.revise(var1, var2):
                if not self.domains[var1]:
                    return False  # Domain wipe-out
                for var3 in self.constraints[var1]:
                    if var3 != var2:
                        queue.append((var3, var1))
        return True


    def is_consistent(self, var, value):
        """
        Check if assigning a value to a variable satisfies all constraints.
        """
        for constraint in self.constraints[var]:
            for other_var, other_value in self.assignments.items():
                if not constraint(value, other_value):
                    return False
        return True

    def revise(self, var1, var2):
        """
        Revise the domain of var1 to enforce arc-consistency.
        """
        revised = False
        for value in self.domains[var1][:]:
            if not any(
                self.is_consistent(var1, value)
                for value2 in self.domains[var2]
                if var2 in self.domains
            ):
                self.domains[var1].remove(value)
                revised = True
        return revised

    def backtrack(self, assignment):
        """
        Perform backtracking search to find a solution.
        """
        if len(assignment) == len(self.variables):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.domains[var]:
            if self.is_consistent(var, value):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result:
                    return result
                del assignment[var]
        return None

    def select_unassigned_variable(self, assignment):
        """
        Select the next variable to assign using Minimum Remaining Values (MRV) heuristic.
        """
        unassigned = [var for var in self.variables if var not in assignment]
        return min(unassigned, key=lambda var: len(self.domains[var]))

    def solve(self):
        """
        Solve the CSP problem.
        """
        self.initialize()
        if not self.ac3():
            return None
        return self.backtrack({})

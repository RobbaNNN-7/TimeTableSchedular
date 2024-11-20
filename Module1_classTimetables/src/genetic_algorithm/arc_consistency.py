"""
                FOR ARC CONSISTENCY - TO POPULATE INITIAL TIME-TABLE
Constraints:
-    Room    : A room cannot be assigned to multiple courses at the same time.
- Instructor : An instructor cannot be assigned to multiple courses at the same time.

Domains:

-   Room Domain     : The list of available rooms.
- Instructor Domain : The list of available instructors.
-  TimeSlot Domain  : The list of available time slots.


USING AC-3 Algorithm
"""

def arc_consistency(variables,domains,constraints):
    queue = [(X,Y) for X in variables for Y in variables if X != Y]

    while queue:
        X,Y = queue.pop(0)
        if revise(X,Y,domains,constraints): # Removes In Consistencies
            if not domains[X]:
                return False   # Not Satisfiable Equation

            for Z in variables:
                if Z != X and (Z,X) in constraints:
                    queue.append((Z,X))



def revise(X,Y,domain,constraints):
    revise = False

    for x in domain[X]:
        if is_consistent(x,y) for y in domain[Y]
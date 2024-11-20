

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

    return True

def revise(X,Y,domain,constraint):
    revise = False
    # Remove InConsistencies
    for value_x in domain[X]:
        if not any(is_consistent(value_x,value_y,constraint) for value_y in domain[Y]):
            domain[X].remove(value_x)
        
        revise = True
    
    return revise

# Check if x,y Satisfy the constraint
def is_consistent(value_x,value_y,constraint):
    return constraint(value_x,value_y)

def populate_time_table(sections,courses,rooms,instructors,time_slots):

    variables = []
    domains = {}
    constraints = {}

    for section in sections:
        for course in courses:
            
            var = f"{course.name} ({section.name})"
            variables.append(var)

            domains[var] = [(time_slot, room, instructor) 
                            for time_slot in time_slots
                            for room in rooms
                            for instructor in instructors]
    

    for X in variables:
        for Y in variables:
            # Assigning Constraints ,
            # x[0] -> time_slot
            # x[1] -> room
            # x[2] -> instructor
            # returns True or False for all X,Y
            constraints[(X,Y)] = lambda x,y: (x[0] != y[0] or x[1] != y[1]) and (x[0] != y[0] or x[2] != y[2])


    # applying Arc-Consistency
    if not arc_consistency(variables,domains,constraints):
        print("Not Found -(arc)")
        return # no TimeTable Found 
    
    
    

    


    




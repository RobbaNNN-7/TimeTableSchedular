from datetime import datetime, timedelta
import pandas as pd

# Generate available timeslots (same as before)
def generate_valid_timeslots(start_date, end_date):
    timeslots = []
    current_date = start_date
    slots = ["10-12", "2-4"]  # Primary slots
    while current_date <= end_date:
        if current_date.weekday() < 5 and current_date.weekday() != 4:  # Exclude Saturdays and keep Friday afternoons free
            for slot in slots:
                timeslots.append({"date": current_date, "slot": slot})
        current_date += timedelta(days=1)
    return timeslots

def enforce_arc_consistency(domains, constraints, subjects):
    queue = []

    # Fill the queue with arcs (pairs of subjects)
    for subject_name, related_subjects in constraints.items():
        for related_subject in related_subjects:
            queue.append((subject_name, related_subject))  # Ensure the queue has pairs

    while queue:
        (subject1, subject2) = queue.pop(0)
        removed = False
        for ts1 in domains[subject1]:
            # Check if there exists a valid timeslot for subject2 that satisfies constraints
            if not any(is_valid_assignment(ts1, ts2, subject1, subject2, subjects) for ts2 in domains[subject2]):
                # Remove invalid timeslot from subject1's domain
                domains[subject1].remove(ts1)
                removed = True

                # If a value was removed, add arcs to the queue for further checking
                for other_subject in constraints[subject1]:
                    if other_subject != subject2:
                        queue.append((other_subject, subject1))

        # If any domain was reduced, enforce arc consistency for other related arcs
        if removed:
            for other_subject in constraints[subject1]:
                if other_subject != subject2:
                    queue.append((subject1, other_subject))



def is_valid_assignment(ts1, ts2, subject1_name, subject2_name, subjects):
    # Find the actual subject dictionaries by subject name from the subjects list
    subject1_dict = next(subject for subject in subjects if subject['name'] == subject1_name)
    subject2_dict = next(subject for subject in subjects if subject['name'] == subject2_name)

    # Now, we can access 'department' and other details
    if subject1_dict['department'] == subject2_dict['department']:
        return ts1 != ts2  # Ensure the same department subjects are not scheduled at the same time
    return True  # Different departments can share the same time




# Solve CSP using domains, forward checking, and arc consistency
def solve_csp(subjects, batch_section_data, timeslots):
    # Initial scheduling and domain setup
    initial_schedule = {}
    global_subject_timeslots = {}
    domains = {subject['name']: [ts for ts in timeslots] for subject in subjects}  # All subjects start with full domains

    # Group subjects by name
    unique_subjects = {}
    for subject in subjects:
        if subject['name'] not in unique_subjects:
            unique_subjects[subject['name']] = []
        unique_subjects[subject['name']].append(subject)

    # Set up constraints (arc consistency)
    constraints = {subject['name']: [] for subject in subjects}
    for subject_name, subject_variants in unique_subjects.items():
        # Check constraints between subjects with the same name (across departments)
        for i, subject_info_1 in enumerate(subject_variants):
            for subject_info_2 in subject_variants[i + 1:]:
                constraints[subject_info_1['name']].append(subject_info_2['name'])
                constraints[subject_info_2['name']].append(subject_info_1['name'])

    # Forward checking to eliminate invalid assignments from domains
    enforce_arc_consistency(domains, constraints,subjects)

    # Track assigned timeslots for each department to avoid conflicts
    department_timeslot_assignment = {subject['department']: {} for subject in subjects}

    # Try to assign timeslots to subjects
    for subject_name, subject_variants in unique_subjects.items():
        assigned = False
        # For subjects with the same name across different departments, they must share the same timeslot
        for ts_date in domains[subject_name]:
            if not assigned:
                
                ts = ts_date  # Get the first valid timeslot from the domain
                valid_assignment = True

                # Check if assigning this timeslot violates the department constraints
                for subject_info in subject_variants:
                    department = subject_info['department']
                    batch = subject_info['batch']
                    
                    # Check if this department already has a timeslot assigned for this timeslot
                    slot_key = f"{ts['date']}_{ts['slot']}"
                    if slot_key in department_timeslot_assignment[department]:
                        valid_assignment = False
                        break

                if valid_assignment:
                    global_subject_timeslots[subject_name] = ts
                    assigned = True

                    # Assign timeslot to all variants of the subject
                    for subject_info in subject_variants:
                        batch = subject_info['batch']
                        department = subject_info['department']
                        
                        # Assign timeslot to batch and department combination
                        key = f"{batch}_{department}_{subject_name}"
                        initial_schedule[key] = {
                            "date": ts["date"].strftime("%Y-%m-%d"),
                            "timeslot": ts["slot"]
                        }

                    # Mark this department as having a subject scheduled in this timeslot
                    for subject_info in subject_variants:
                        department = subject_info['department']
                        department_timeslot_assignment[department][slot_key] = subject_name

                    break
        
        if not assigned:
            print(f"Warning: No available timeslots left for subject {subject_name}!")

    return initial_schedule
from datetime import datetime, timedelta
import pandas as pd

def generate_valid_timeslots(start_date, end_date):
    timeslots = []
    current_date = start_date
    slots = ["10-12", "2-4"]
    while current_date <= end_date:
        if current_date.weekday() < 6:  
            for slot in slots:
                timeslots.append({"date": current_date, "slot": slot})
        current_date += timedelta(days=1)
    return timeslots

def enforce_arc_consistency(domains, constraints, subjects):
    queue = []
    for subject_name, related_subjects in constraints.items():
        for related_subject in related_subjects:
            queue.append((subject_name, related_subject))

    while queue:
        (subject1, subject2) = queue.pop(0)
        removed = False
        domain_copy = domains[subject1].copy()
        
        for ts1 in domain_copy:
            if not any(is_valid_assignment(ts1, ts2, subject1, subject2, subjects) 
                      for ts2 in domains[subject2]):
                domains[subject1].remove(ts1)
                removed = True
                
                for other_subject in constraints[subject1]:
                    if other_subject != subject2:
                        queue.append((other_subject, subject1))
                        
        if removed and len(domains[subject1]) == 0:
            return False  # No valid assignments possible
            
    return True

def is_valid_assignment(ts1, ts2, subject1_name, subject2_name, subjects):
    try:
        subject1_dict = next(subject for subject in subjects if subject['name'] == subject1_name)
        subject2_dict = next(subject for subject in subjects if subject['name'] == subject2_name)
        
        # Same department subjects can't be at same time
        if subject1_dict['department'] == subject2_dict['department']:
            return ts1['date'] != ts2['date'] or ts1['slot'] != ts2['slot']
            
        # Same name subjects must be at same time
        if subject1_name == subject2_name:
            return ts1['date'] == ts2['date'] and ts1['slot'] == ts2['slot']
            
        return True
    except (StopIteration, KeyError) as e:
        print(f"Error in valid_assignment check: {e}")
        return False

def solve_csp(subjects, batch_section_data, timeslots):
    initial_schedule = {}
    global_subject_timeslots = {}
    domains = {subject['name']: timeslots.copy() for subject in subjects}

    # constraints setup
    constraints = {subject['name']: [] for subject in subjects}
    departments = {}
    
    # Group subjects by department
    for subject in subjects:
        if subject['department'] not in departments:
            departments[subject['department']] = []
        departments[subject['department']].append(subject['name'])
    
    # Set up constraints between all subjects in same department
    for dept_subjects in departments.values():
        for i, subject1 in enumerate(dept_subjects):
            for subject2 in dept_subjects[i+1:]:
                constraints[subject1].append(subject2)
                constraints[subject2].append(subject1)
    
    # Add constraints for same-name subjects
    unique_subjects = {}
    for subject in subjects:
        if subject['name'] not in unique_subjects:
            unique_subjects[subject['name']] = []
        unique_subjects[subject['name']].append(subject)
        
    for subject_variants in unique_subjects.values():
        if len(subject_variants) > 1:
            for i, subject1 in enumerate(subject_variants):
                for subject2 in subject_variants[i+1:]:
                    constraints[subject1['name']].append(subject2['name'])
                    constraints[subject2['name']].append(subject1['name'])

    if not enforce_arc_consistency(domains, constraints, subjects):
        return None  # No valid solution possible

    department_timeslot_assignment = {subject['department']: {} for subject in subjects}

    for subject_name, subject_variants in unique_subjects.items():
        valid_timeslot = None
        
        for ts in domains[subject_name]:
            valid = True
            slot_key = f"{ts['date']}_{ts['slot']}"
            
            for subject_info in subject_variants:
                department = subject_info['department']
                if slot_key in department_timeslot_assignment[department]:
                    valid = False
                    break
                    
            if valid:
                valid_timeslot = ts
                break
                
        if valid_timeslot:
            global_subject_timeslots[subject_name] = valid_timeslot
            
            for subject_info in subject_variants:
                batch = subject_info['batch']
                department = subject_info['department']
                key = f"{batch}_{department}_{subject_name}"
                initial_schedule[key] = {
                    "date": valid_timeslot["date"].strftime("%Y-%m-%d"),
                    "timeslot": valid_timeslot["slot"]
                }
                slot_key = f"{valid_timeslot['date']}_{valid_timeslot['slot']}"
                department_timeslot_assignment[department][slot_key] = subject_name
        else:
            print(f"Warning: No valid timeslot found for {subject_name}")
            return None

    return initial_schedule
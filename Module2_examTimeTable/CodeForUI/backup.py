import json
from datetime import datetime, timedelta
import random
import copy

def generate_valid_timeslots(start_date, end_date):
    timeslots = []
    current_date = start_date
    slots = ["10-12", "2-4"]  # Primary slot
    while current_date <= end_date:
        # Exclude Saturdays and keep Friday afternoons free
        if current_date.weekday() < 5 and current_date.weekday() != 4:
            for slot in slots:
                timeslots.append({"date": current_date, "slot": slot})
        current_date += timedelta(days=1)
    return timeslots

def solve_csp(subjects, batch_section_data, timeslots):
    # Initial scheduling
    initial_schedule = {}
    global_subject_timeslots = {}

    # Group subjects by their unique name (subjects with the same name may belong to different departments)
    unique_subjects = {}
    for subject in subjects:
        if subject['name'] not in unique_subjects:
            unique_subjects[subject['name']] = []
        unique_subjects[subject['name']].append(subject)

    # Track available timeslots for each day
    available_timeslots = {slot["date"]: [] for slot in timeslots}
    for slot in timeslots:
        available_timeslots[slot["date"]].append(slot)

    # Track assigned timeslots per department to avoid double-booking within the department
    department_timeslot_assignment = {subject['department']: {} for subject in subjects}

    # Assign timeslots to subjects
    for subject_name, subject_variants in unique_subjects.items():
        assigned = False
        # If multiple subjects from different departments share the same name, they must share the same timeslot.
        for ts_date in available_timeslots:
            if not assigned:
                if available_timeslots[ts_date]:
                    # Try to assign a timeslot
                    for ts in available_timeslots[ts_date]:
                        # If the subject is from the same department, we need unique timeslots
                        departments_assigned = [subject['department'] for subject in subject_variants]
                        
                        # Check if any department has already been assigned the same timeslot on this day
                        valid = True
                        for department in departments_assigned:
                            slot_key = f"{ts['date']}_{ts['slot']}"
                            if slot_key in department_timeslot_assignment[department]:
                                valid = False
                                break
                        if valid:
                            # Assign the same timeslot for all subjects with the same name across departments
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
                            for department in departments_assigned:
                                department_timeslot_assignment[department][slot_key] = subject_name
                            
                            break

            if assigned:
                break
        
        if not assigned:
            print(f"Warning: No available timeslots left for subject {subject_name}!")

    return initial_schedule






def optimize_schedule_ga(initial_schedule, subjects, batch_section_data, timeslots):
    def calculate_fitness(schedule):
        penalties = 0
        batch_dates = {}
        subject_dates = {}

        for key, details in schedule.items():
            batch = key.split('_')[0]
            subject = key.split('_')[2]  # Adjusted for batch_department_subject format
            exam_date = details['date']
            exam_day = datetime.strptime(exam_date, "%Y-%m-%d").weekday()

            # Penalty for Saturday exams
            if exam_day == 5:
                penalties += 100

            # Penalty for Friday afternoon exams (2-4 slot)
            if exam_day == 4 and details['timeslot'] == "2-4":
                penalties += 50

            # Penalty for multiple exams of a batch on same day
            if batch not in batch_dates:
                batch_dates[batch] = {}

            if exam_date in batch_dates[batch]:
                penalties += 100  # High penalty for multiple exams on same day
            else:
                batch_dates[batch][exam_date] = subject

            # Ensure spread of subjects
            if subject not in subject_dates:
                subject_dates[subject] = set()
            subject_dates[subject].add(exam_date)

        return -penalties  # Negative because GA typically maximizes fitness

    def crossover(parent1, parent2):
        offspring = copy.deepcopy(parent1)
        for key in parent2:
            if random.random() < 0.5:
                offspring[key] = parent2[key]
        return offspring

    def mutate(schedule, mutation_rate=0.1):
        mutated = copy.deepcopy(schedule)
        for key in mutated:
            if random.random() < mutation_rate:
                # Randomly select a new timeslot
                new_timeslot = random.choice(timeslots)
                mutated[key]['date'] = new_timeslot['date'].strftime("%Y-%m-%d")
                mutated[key]['timeslot'] = new_timeslot['slot']
        return mutated

    # Genetic Algorithm parameters
    population_size = 50
    generations = 100
    elite_size = 5

    # Initialize population
    population = [initial_schedule]
    for _ in range(population_size - 1):
        population.append(mutate(initial_schedule))

    # Evolution
    for _ in range(generations):
        # Evaluate fitness
        fitness_scores = [calculate_fitness(ind) for ind in population]
        
        # Select parents
        parents = [population[i] for i in sorted(range(len(fitness_scores)), key=lambda k: fitness_scores[k], reverse=True)]
        
        # Create next generation
        next_generation = parents[:elite_size]
        
        while len(next_generation) < population_size:
            parent1 = random.choice(parents[:10])
            parent2 = random.choice(parents[:10])
            offspring = crossover(parent1, parent2)
            offspring = mutate(offspring)
            next_generation.append(offspring)
        
        population = next_generation

    # Return best solution
    return max(population, key=calculate_fitness)

def main():
    # Read the input JSON file
    filename = "haha.json"
    
    with open(filename, 'r') as file:
        data = json.load(file)
    
    # Convert the dates from strings to datetime objects
    start_date = datetime.strptime(data["startDate"], "%Y-%m-%d")
    end_date = datetime.strptime(data["endDate"], "%Y-%m-%d")
    
    # Generate the available timeslots
    timeslots = generate_valid_timeslots(start_date, end_date)

    # Generate schedule using the CSP solver
    schedule = solve_csp(
        data['subjects'], 
        data['batchSections'], 
        timeslots
    )

    # Print the initial schedule
    print("\nInitial Exam Schedule:")
    print(json.dumps(schedule, indent=4))


    # Optionally, optimize the schedule using the genetic algorithm
    optimized_schedule = optimize_schedule_ga(schedule, data['subjects'], data['batchSections'], timeslots)

    # Print the optimized schedule
    print("\nOptimized Exam Schedule:")
    print(json.dumps(optimized_schedule, indent=4))


if __name__ == '__main__':
    main()

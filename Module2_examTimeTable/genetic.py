from genetic_utils import *
from csp import *
import random
import copy

class GeneticAlgorithm:
    def __init__(self, initial_schedule, start_date, end_date, population_size=20, generations=1500, mutation_rate=0.1):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.population = [Individual(copy.deepcopy(initial_schedule)) for _ in range(population_size)]

    

    # In genetic.py
    def crossover(self, parent1, parent2):
        child_chromosome = {}
        keys = list(parent1.chromosome.keys())
        
        # Track dates and timeslots by batch and department
        batch_dept_schedule = {}
        
        # First, copy a random selection of genes from parent1 
        # (these are guaranteed to be valid since parent1 is valid)
        for key in keys:
            if random.random() < 0.5:
                child_chromosome[key] = copy.deepcopy(parent1.chromosome[key])
                parts = key.split("_")
                batch_dept = f"{parts[0]}_{parts[1]}"
                if batch_dept not in batch_dept_schedule:
                    batch_dept_schedule[batch_dept] = {
                        'slots': set(),  # Track date+timeslot combinations
                        'dates': set()   # Track dates
                    }
                schedule_key = f"{child_chromosome[key]['date']}_{child_chromosome[key]['timeslot']}"
                batch_dept_schedule[batch_dept]['slots'].add(schedule_key)
                batch_dept_schedule[batch_dept]['dates'].add(child_chromosome[key]['date'])

        # Then fill remaining genes only with valid slots
        for key in keys:
            if key not in child_chromosome:
                parts = key.split("_")
                batch_dept = f"{parts[0]}_{parts[1]}"
                
                if batch_dept not in batch_dept_schedule:
                    # If no previous exams for this batch+dept, can use parent2's slot
                    child_chromosome[key] = copy.deepcopy(parent2.chromosome[key])
                    batch_dept_schedule[batch_dept] = {
                        'slots': {f"{child_chromosome[key]['date']}_{child_chromosome[key]['timeslot']}"},
                        'dates': {child_chromosome[key]['date']}
                    }
                else:
                    # Find valid slot that doesn't conflict
                    valid_slots = []
                    current = self.start_date
                    while current <= self.end_date:
                        date_str = current.strftime("%Y-%m-%d")
                        for timeslot in ["10-12", "2-4"]:
                            test_key = f"{date_str}_{timeslot}"
                            if (test_key not in batch_dept_schedule[batch_dept]['slots'] and 
                                date_str not in batch_dept_schedule[batch_dept]['dates']):
                                valid_slots.append((date_str, timeslot))
                        current += timedelta(days=1)
                    
                    if valid_slots:
                        chosen_date, chosen_timeslot = random.choice(valid_slots)
                        child_chromosome[key] = copy.deepcopy(parent2.chromosome[key])
                        child_chromosome[key]["date"] = chosen_date
                        child_chromosome[key]["timeslot"] = chosen_timeslot
                        
                        schedule_key = f"{chosen_date}_{chosen_timeslot}"
                        batch_dept_schedule[batch_dept]['slots'].add(schedule_key)
                        batch_dept_schedule[batch_dept]['dates'].add(chosen_date)
                    else:
                        # If no valid slots found, keep parent1's gene
                        # (which we know is valid)
                        child_chromosome[key] = copy.deepcopy(parent1.chromosome[key])
        
        return Individual(child_chromosome)

    def mutate(self, individual):
        mutated_chromosome = copy.deepcopy(individual.chromosome)
        keys = list(mutated_chromosome.keys())
        
        # Track schedule by batch, department, date and timeslot
        batch_dept_schedules = {}
        
        # First, build current schedule
        for key in keys:
            parts = key.split("_")
            batch_dept = f"{parts[0]}_{parts[1]}"
            if batch_dept not in batch_dept_schedules:
                batch_dept_schedules[batch_dept] = {
                    'date_slots': set(),  # Track date+timeslot combinations
                    'dates': set()        # Track just dates for same-day check
                }
                
            current_date = mutated_chromosome[key]["date"]
            current_slot = mutated_chromosome[key]["timeslot"]
            schedule_key = f"{current_date}_{current_slot}"
            
            batch_dept_schedules[batch_dept]['date_slots'].add(schedule_key)
            batch_dept_schedules[batch_dept]['dates'].add(current_date)
        
        # Now do mutations
        for key in keys:
            if random.random() < self.mutation_rate:
                parts = key.split("_")
                batch_dept = f"{parts[0]}_{parts[1]}"
                
                # Get current schedule
                current_date = mutated_chromosome[key]["date"]
                current_slot = mutated_chromosome[key]["timeslot"]
                current_key = f"{current_date}_{current_slot}"
                
                # Remove current schedule from tracking
                if current_key in batch_dept_schedules[batch_dept]['date_slots']:
                    batch_dept_schedules[batch_dept]['date_slots'].remove(current_key)
                if current_date in batch_dept_schedules[batch_dept]['dates']:
                    batch_dept_schedules[batch_dept]['dates'].remove(current_date)
                
                # Try to find a valid new slot that doesn't violate constraints
                valid_slots = []
                current = self.start_date
                while current <= self.end_date:
                    date_str = current.strftime("%Y-%m-%d")
                    for timeslot in ["10-12", "2-4"]:
                        test_key = f"{date_str}_{timeslot}"
                        # Check both time slot conflict and same-day constraint
                        if (test_key not in batch_dept_schedules[batch_dept]['date_slots'] and
                            (date_str not in batch_dept_schedules[batch_dept]['dates'] or
                            len(batch_dept_schedules[batch_dept]['dates']) == 0)):
                            valid_slots.append((date_str, timeslot))
                    current += timedelta(days=1)
                
                if valid_slots:
                    # Pick new slot and update
                    new_date, new_timeslot = random.choice(valid_slots)
                    new_key = f"{new_date}_{new_timeslot}"
                    
                    mutated_chromosome[key]["date"] = new_date
                    mutated_chromosome[key]["timeslot"] = new_timeslot
                    
                    # Update tracking
                    batch_dept_schedules[batch_dept]['date_slots'].add(new_key)
                    batch_dept_schedules[batch_dept]['dates'].add(new_date)
                else:
                    # If no valid slot found, keep original schedule
                    batch_dept_schedules[batch_dept]['date_slots'].add(current_key)
                    batch_dept_schedules[batch_dept]['dates'].add(current_date)
                    mutated_chromosome[key]["date"] = current_date
                    mutated_chromosome[key]["timeslot"] = current_slot
        
        return Individual(mutated_chromosome)

    def run(self):
        # Main GA loop
        for generation in range(self.generations):
            # Evaluate fitness and sort population
            self.population.sort(key=lambda ind: ind.fitness, reverse=True)

            # Elitism: Preserve the top individuals
            next_generation = self.population[:5]  # Keep top 5 individuals

            # Generate the rest of the next generation using tournament selection
            while len(next_generation) < self.population_size:
                # Tournament selection
                tournament_size = 5
                tournament = random.sample(self.population, tournament_size)
                parent1 = max(tournament, key=lambda ind: ind.fitness)
                tournament = random.sample(self.population, tournament_size)
                parent2 = max(tournament, key=lambda ind: ind.fitness)
                
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                next_generation.append(child)

            self.population = next_generation

        # Return the best schedule from the final population
        return self.population[0].chromosome





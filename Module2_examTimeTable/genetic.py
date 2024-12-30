from genetic_utils import *
from csp import *
import random
import copy
from datetime import datetime, timedelta

class GeneticAlgorithm:
    def __init__(self, initial_schedule, start_date, end_date, population_size=50, generations=600, mutation_rate=0.1):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.population = [Individual(copy.deepcopy(initial_schedule)) for _ in range(population_size)]

    def validate_schedule(self, schedule, batch_dept, date, timeslot):
        """
        Validates if a given schedule slot is valid for a batch_dept
        Returns True if valid, False if conflicts exist
        """
        schedule_key = f"{date}_{timeslot}"
        
        # Check all existing exams for this batch_dept
        for key, exam in schedule.items():
            parts = key.split("_")
            current_batch_dept = f"{parts[0]}_{parts[1]}"
            
            if current_batch_dept == batch_dept:
                # Check for same time slot conflict
                if exam['date'] == date and exam['timeslot'] == timeslot:
                    return False
                # Check for same day conflict
                if exam['date'] == date:
                    return False
        return True

    def get_valid_slot(self, schedule, batch_dept):
        """
        Finds a valid slot for a given batch_dept that doesn't violate constraints
        """
        valid_slots = []
        current = self.start_date
        
        while current <= self.end_date:
            date_str = current.strftime("%Y-%m-%d")
            for timeslot in ["10-12", "2-4"]:
                if self.validate_schedule(schedule, batch_dept, date_str, timeslot):
                    valid_slots.append((date_str, timeslot))
            current += timedelta(days=1)
        
        return random.choice(valid_slots) if valid_slots else None

    def crossover(self, parent1, parent2):
        child_chromosome = {}
        keys = list(parent1.chromosome.keys())
        
        # First phase: Copy random selection from parent1
        for key in keys:
            if random.random() < 0.5:
                child_chromosome[key] = copy.deepcopy(parent1.chromosome[key])
        
        # Second phase: Fill remaining slots with valid assignments
        for key in keys:
            if key not in child_chromosome:
                parts = key.split("_")
                batch_dept = f"{parts[0]}_{parts[1]}"
                
                # Try parent2's slot first
                parent2_slot = parent2.chromosome[key]
                if self.validate_schedule(child_chromosome, batch_dept, 
                                       parent2_slot['date'], parent2_slot['timeslot']):
                    child_chromosome[key] = copy.deepcopy(parent2_slot)
                else:
                    # Find a new valid slot
                    valid_slot = self.get_valid_slot(child_chromosome, batch_dept)
                    if valid_slot:
                        date, timeslot = valid_slot
                        child_chromosome[key] = {
                            'date': date,
                            'timeslot': timeslot
                        }
                    else:
                        # If no valid slot found, use parent1's slot
                        child_chromosome[key] = copy.deepcopy(parent1.chromosome[key])
        
        return Individual(child_chromosome)

    def mutate(self, individual):
        mutated_chromosome = copy.deepcopy(individual.chromosome)
        keys = list(mutated_chromosome.keys())
        
        for key in keys:
            if random.random() < self.mutation_rate:
                parts = key.split("_")
                batch_dept = f"{parts[0]}_{parts[1]}"
                
                # Temporarily remove current exam for proper validation
                current_exam = mutated_chromosome.pop(key)
                
                # Find new valid slot
                valid_slot = self.get_valid_slot(mutated_chromosome, batch_dept)
                
                if valid_slot:
                    date, timeslot = valid_slot
                    mutated_chromosome[key] = {
                        'date': date,
                        'timeslot': timeslot
                    }
                else:
                    # If no valid slot found, restore original
                    mutated_chromosome[key] = current_exam
        
        return Individual(mutated_chromosome)

    def run(self):
        for generation in range(self.generations):
            self.population.sort(key=lambda ind: ind.fitness, reverse=True)
            next_generation = self.population[:2]  # Elitism
            
            while len(next_generation) < self.population_size:
                parent1, parent2 = random.sample(self.population[:10], 2)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                next_generation.append(child)
            
            self.population = next_generation
        
        return self.population[0].chromosome





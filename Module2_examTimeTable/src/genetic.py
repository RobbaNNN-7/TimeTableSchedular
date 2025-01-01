from src.genetic_utils import *
import random
import copy
from datetime import datetime, timedelta

class GeneticAlgorithm:
    def __init__(self, initial_schedule, start_date, end_date, population_size=50, generations=1000, mutation_rate=0.2):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.population = [Individual(copy.deepcopy(initial_schedule)) for _ in range(population_size)]

    def validate_schedule(self, schedule, batch_dept, date, timeslot):
        """
        Enhanced validation with stricter constraints
        """
        proposed_batch, proposed_dept = batch_dept.split("_")

        # Check all existing exams for conflicts
        for key, exam in schedule.items():
            exam_date = exam['date']
            exam_timeslot = exam['timeslot']
            current_batch, current_dept, _ = key.split("_")  # Split into batch, dept, subject

            # Rule 1: Same batch+department cannot have exams on same day
            if current_batch == proposed_batch and current_dept == proposed_dept:
                if exam_date == date:
                    return False

            # Rule 2: Same department cannot have overlapping timeslots on same day
            if current_dept == proposed_dept and exam_date == date and exam_timeslot == timeslot:
                return False

        return True

    def get_valid_slot(self, schedule, batch_dept):
        """
        Enhanced slot selection with better distribution
        """
        valid_slots = []
        current = self.start_date
        
        # Get all possible slots
        while current <= self.end_date:
            date_str = current.strftime("%Y-%m-%d")
            for timeslot in ["10-12", "2-4"]:
                if self.validate_schedule(schedule, batch_dept, date_str, timeslot):
                    # Calculate how many exams are already on this date
                    exams_on_date = sum(1 for exam in schedule.values() if exam['date'] == date_str)
                    # Add slot multiple times inversely proportional to number of exams
                    # This promotes better distribution
                    weight = max(1, 5 - exams_on_date)
                    for _ in range(weight):
                        valid_slots.append((date_str, timeslot))
            current += timedelta(days=1)
        
        return random.choice(valid_slots) if valid_slots else None

    def crossover(self, parent1, parent2):
        child_chromosome = {}
        keys = list(parent1.chromosome.keys())
        random.shuffle(keys)  # Randomize order to avoid bias
        
        # Try to fill slots in random order
        for key in keys:
            parts = key.split("_")
            batch_dept = f"{parts[0]}_{parts[1]}"
            
            # Try parent1's slot first
            if self.validate_schedule(child_chromosome, batch_dept, 
                                   parent1.chromosome[key]['date'], 
                                   parent1.chromosome[key]['timeslot']):
                child_chromosome[key] = copy.deepcopy(parent1.chromosome[key])
                continue
                
            # Try parent2's slot next
            if self.validate_schedule(child_chromosome, batch_dept,
                                   parent2.chromosome[key]['date'],
                                   parent2.chromosome[key]['timeslot']):
                child_chromosome[key] = copy.deepcopy(parent2.chromosome[key])
                continue
                
            # If neither parent slot works, find a new valid slot
            valid_slot = self.get_valid_slot(child_chromosome, batch_dept)
            if valid_slot:
                date, timeslot = valid_slot
                child_chromosome[key] = {
                    'date': date,
                    'timeslot': timeslot
                }
            else:
                # If no valid slot found, try to shift existing assignments
                self.shift_assignments(child_chromosome, key, batch_dept)
        
        return Individual(child_chromosome)

    def shift_assignments(self, chromosome, new_key, batch_dept):
        """
        Attempts to shift existing assignments to accommodate a new exam
        """
        # Try each day in range
        current = self.start_date
        while current <= self.end_date:
            date_str = current.strftime("%Y-%m-%d")
            for timeslot in ["10-12", "2-4"]:
                # Create a temporary schedule to test shifts
                temp_schedule = copy.deepcopy(chromosome)
                
                # Try to move conflicting exams
                conflicts_resolved = True
                for key, exam in list(temp_schedule.items()):
                    if exam['date'] == date_str and exam['timeslot'] == timeslot:
                        # Try to find new slot for conflicting exam
                        conflict_batch_dept = "_".join(key.split("_")[:2])
                        new_slot = self.get_valid_slot(temp_schedule, conflict_batch_dept)
                        if new_slot:
                            temp_schedule[key] = {
                                'date': new_slot[0],
                                'timeslot': new_slot[1]
                            }
                        else:
                            conflicts_resolved = False
                            break
                
                if conflicts_resolved:
                    # If we successfully moved all conflicts, use this arrangement
                    chromosome.clear()
                    chromosome.update(temp_schedule)
                    chromosome[new_key] = {
                        'date': date_str,
                        'timeslot': timeslot
                    }
                    return
            
            current += timedelta(days=1)

    def mutate(self, individual):
        mutated_chromosome = copy.deepcopy(individual.chromosome)
        keys = list(mutated_chromosome.keys())
        random.shuffle(keys)
        
        for key in keys:
            if random.random() < self.mutation_rate:
                parts = key.split("_")
                batch_dept = f"{parts[0]}_{parts[1]}"
                
                # Temporarily remove current exam
                current_exam = mutated_chromosome.pop(key)
                
                # Try to find a new valid slot
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
        best_fitness = float('-inf')
        best_solution = None
        generations_without_improvement = 0
        
        for generation in range(self.generations):
            self.population.sort(key=lambda ind: ind.fitness, reverse=True)
            
            current_best = self.population[0]
            if current_best.fitness > best_fitness:
                best_fitness = current_best.fitness
                best_solution = copy.deepcopy(current_best.chromosome)
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1
            
            # Early stopping if stuck
            if generations_without_improvement > 150:
                break
                
            # Keep top performers
            next_generation = self.population[:3]
            
            # Create rest of new generation
            while len(next_generation) < self.population_size:
                # Tournament selection
                tournament_size = 5
                candidates = random.sample(self.population, tournament_size)
                parent1 = max(candidates, key=lambda ind: ind.fitness)
                candidates = random.sample(self.population, tournament_size)
                parent2 = max(candidates, key=lambda ind: ind.fitness)
                
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                next_generation.append(child)
            
            self.population = next_generation
        
        return best_solution
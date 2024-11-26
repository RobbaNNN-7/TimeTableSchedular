from genetic_utils import *
from csp import *
import random
import copy

class GeneticAlgorithm:
    def __init__(self, initial_schedule, population_size=20, generations=100, mutation_rate=0.1):
        # Initialize GA parameters
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

        # Start with an initial population based on the CSP schedule
        self.population = [Individual(copy.deepcopy(initial_schedule)) for _ in range(population_size)]

    def crossover(self, parent1, parent2):
        # Perform single-point crossover
        child_chromosome = {}
        crossover_point = random.randint(0, len(parent1.chromosome) - 1)
        keys = list(parent1.chromosome.keys())

        for i, key in enumerate(keys):
            if i < crossover_point:
                child_chromosome[key] = parent1.chromosome[key]
            else:
                child_chromosome[key] = parent2.chromosome[key]

        return Individual(child_chromosome)

    def mutate(self, individual):
        # Perform mutation while respecting hard constraints
        mutated_chromosome = copy.deepcopy(individual.chromosome)
        keys = list(mutated_chromosome.keys())

        for key in keys:
            if random.random() < self.mutation_rate:
                # Change the timeslot for this exam
                mutated_chromosome[key]["timeslot"] = random.choice(["10-12", "2-4"])
                new_date = datetime.strptime(mutated_chromosome[key]["date"], "%Y-%m-%d") + timedelta(days=random.randint(-2, 2))
                mutated_chromosome[key]["date"] = new_date.strftime("%Y-%m-%d")

        return Individual(mutated_chromosome)

    def run(self):
        # Main GA loop
        for generation in range(self.generations):
            # Evaluate fitness and sort population
            self.population.sort(key=lambda ind: ind.fitness, reverse=True)

            # Elitism: Preserve the top individuals
            next_generation = self.population[:2]

            # Generate the rest of the next generation
            while len(next_generation) < self.population_size:
                parent1, parent2 = random.sample(self.population[:10], 2)  # Select from the top 10 individuals
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                next_generation.append(child)

            self.population = next_generation

            # Print the best fitness in the current generation
            #print(f"Generation {generation + 1}: Best Fitness = {self.population[0].fitness}")

        # Return the best schedule from the final population
        return self.population[0].chromosome





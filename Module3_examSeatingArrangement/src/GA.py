from collections import defaultdict, deque
from typing import List
from src.classes.Student import *
from src.classes.Classroom import *
import random

class GeneticAlgorithm:
    

    def __init__(self, students: List[Student], classrooms: List[Classroom]):
        self.PopulationCount = 200
        self.population = []
        self.students = students
        self.classrooms = classrooms

    def generate_initial_population(self):
        """
        Generates an initial population of chromosomes.
        
        Returns:
            list: A list of chromosomes (each chromosome is a list of classroom arrangements).
        """
        for _ in range(self.PopulationCount):
            # Create a deep copy of the classrooms to start a fresh arrangement
            arrangement = [Classroom(c.name, c.num_columns, c.seats_per_column) for c in self.classrooms]
            
            # Shuffle students for random assignment
            shuffled_students = self.students[:]
            random.shuffle(shuffled_students)
            
            # Assign students to classrooms
            student_index = 0
            for classroom in arrangement:
                for column in range(classroom.num_columns):
                    while classroom.is_seat_available(column) and student_index < len(shuffled_students):
                        classroom.assign_student(column, shuffled_students[student_index])
                        student_index += 1
            
            # Add this arrangement as a chromosome
            self.population.append(arrangement)
    
    def calculate_fitness(self,chromosome):
        """
        Calculate the fitness of a chromosome.
        
        Args:
            chromosome (list[Classroom]): The seating arrangement for all classrooms.
        
        Returns:
            float: The fitness score of the chromosome.
        """
        hard_penalty = 0
        soft_reward = 0
        
        # Track all student IDs to ensure no repetitions
        seen_students = set()
        
        for classroom in chromosome:
            # Check adjacent column constraint
            for col in range(len(classroom.seating)):
                subjects_current = {student.subject for student in classroom.seating[col]}
                
                # Check the column to the left
                if col - 1 >= 0:
                    subjects_left = {student.subject for student in classroom.seating[col - 1]}
                    if not subjects_current.isdisjoint(subjects_left):
                        hard_penalty += 100  # Penalty for subject clash with left column
                
                # Check the column to the right
                if col + 1 < len(classroom.seating):
                    subjects_right = {student.subject for student in classroom.seating[col + 1]}
                    if not subjects_current.isdisjoint(subjects_right):
                        hard_penalty += 100  # Penalty for subject clash with right column

            for column in classroom.seating:
                # Check for skipped seats in columns
                if "" in column[:-1]:
                    hard_penalty += 50  # Penalty for skipped seats
                
                # Reward clustering by section/department
                sections = {student.section for student in column}
                departments = {student.department for student in column}
                if len(sections) == 1:  # All students in the column from the same section
                    soft_reward += 10
                if len(departments) == 1:  # All students in the column from the same department
                    soft_reward += 10
                
                # Ensure no student repetition
                for student in column:
                    if student.student_id in seen_students:
                        hard_penalty += 100  # Penalty for student repetition
                    else:
                        seen_students.add(student.student_id)
        
        

        
        # Reward balanced classroom utilization
        total_students = sum(len(column) for classroom in chromosome for column in classroom.seating)
        average_students_per_classroom = total_students / len(chromosome)
        for classroom in chromosome:
            classroom_students = sum(len(column) for column in classroom.seating)
            if classroom_students >= 0.8 * average_students_per_classroom:
                soft_reward += 20  # Reward for good utilization
            elif classroom_students <= 0.5 * average_students_per_classroom:
                hard_penalty += 30  # Penalty for underutilized classroom
        
        # Fitness score: maximize reward, minimize penalty
        fitness_score = -hard_penalty + soft_reward
        return fitness_score



    def roulette_wheel_selection(self, fitness_scores, num_selected):
        """
        Perform roulette wheel selection.
        
        Args:
            population (list): List of chromosomes.
            fitness_scores (list[float]): Fitness scores corresponding to the population.
            num_selected (int): Number of chromosomes to select.
        
        Returns:
            list: Selected chromosomes.
        """
        # Normalize fitness scores to ensure all are positive
        min_fitness = min(fitness_scores)
        if min_fitness < 0:
            fitness_scores = [score - min_fitness for score in fitness_scores]
        
        # Calculate total fitness and probabilities
        total_fitness = sum(fitness_scores)
        probabilities = [1/len(fitness_scores) for _ in fitness_scores] if total_fitness == 0 else [score / total_fitness for score in fitness_scores]
        
        # Create cumulative probability distribution
        cumulative_probs = []
        cumulative_sum = 0
        for prob in probabilities:
            cumulative_sum += prob
            cumulative_probs.append(cumulative_sum)
        
        # Perform selection
        selected = []
        for _ in range(num_selected):
            r = random.random()  # Random number between 0 and 1
            for i, cumulative_prob in enumerate(cumulative_probs):
                if r <= cumulative_prob:
                    selected.append(self.population[i])
                    break
        
        return selected
    
    def one_point_crossover(self, parent1, parent2):
        """
        Perform one-point crossover at the student level.

        Args:
            parent1 (list[Classroom]): The first parent chromosome (list of Classroom objects).
            parent2 (list[Classroom]): The second parent chromosome (list of Classroom objects).

        Returns:
            tuple: Two offspring chromosomes (lists of Classroom objects).
        """
        assert len(parent1) == len(parent2), "Parent chromosomes must have the same number of classrooms"

        # Random crossover points
        crossover_point_class = random.randint(0, len(parent1) - 1)
        crossover_point_column = random.randint(0, parent2[crossover_point_class].num_columns - 1)
        crossover_point_student = random.randint(0, parent2[crossover_point_class].seats_per_column - 1)

        # Helper function to copy classrooms up to the crossover point
        def copy_up_to_crossover(parent, crossover_class, crossover_col, crossover_student):
            offspring = [Classroom(c.name, c.num_columns, c.seats_per_column) for c in parent]
            for i in range(crossover_class + 1):
                if i < crossover_class:
                    offspring[i].seating = [list(col) for col in parent[i].seating]
                elif i == crossover_class:
                    for j in range(crossover_col + 1):
                        if j < crossover_col:
                            offspring[i].seating[j] = list(parent[i].seating[j])
                        else:
                            offspring[i].seating[j] = parent[i].seating[j][:crossover_student + 1]
            return offspring

        # Helper function to assign remaining students
        def assign_remaining_students(source_parent, offspring):
            for classroom in source_parent:
                for col in classroom.seating:
                    for student in col:
                        if not any(
                            student.student_id == other_student.student_id
                            for c in offspring
                            for col in c.seating
                            for other_student in col
                        ):
                            assigned = False
                            for target_classroom in offspring:
                                for col_no in range(target_classroom.num_columns):
                                    if target_classroom.is_seat_available(col_no):
                                        target_classroom.assign_student(col_no, student)
                                        assigned = True
                                        break
                                if assigned:
                                    break

        # Create offspring1 and offspring2
        offspring1 = copy_up_to_crossover(parent2, crossover_point_class, crossover_point_column, crossover_point_student)
        assign_remaining_students(parent1, offspring1)

        offspring2 = copy_up_to_crossover(parent1, crossover_point_class, crossover_point_column, crossover_point_student)
        assign_remaining_students(parent2, offspring2)

        return offspring1, offspring2


    def multiple_swaps_mutation(self,chromosome):
        """
        Perform mutation by swapping two randomly selected students within the arrangement.

        Args:
            chromosome (list[Classroom]): A single chromosome (list of Classroom objects).

        Returns:
            list[Classroom]: The mutated chromosome.
        """
        # Flatten all students with their locations for easier random selection
        student_positions = []
        for class_idx, classroom in enumerate(chromosome):
            for col_idx, column in enumerate(classroom.seating):
                for row_idx, student in enumerate(column):
                    if student:  # Ensure only valid students are considered
                        student_positions.append((class_idx, col_idx, row_idx, student))
        '''
        # Debug: Log all students before mutation
        print("\nBefore Mutation:")
        for class_idx, classroom in enumerate(chromosome):
            for col_idx, column in enumerate(classroom.seating):
                for row_idx, student in enumerate(column):
                    print(f"Classroom {class_idx}, Seat ({col_idx},{row_idx}): {student}")
        '''
        # Ensure there are at least two students to swap
        if len(student_positions) < 2:
            return chromosome  # No mutation possible

        # Perform multiple swaps (can be set to a specific number of swaps)
        num_swaps = len(chromosome)
        for _ in range(1):
            # Randomly select two different students
            pos1, pos2 = random.sample(student_positions, 2)

            
            # Unpack positions
            class1, col1, row1, student1 = pos1
            class2, col2, row2, student2 = pos2
            '''
            # Debug: Log positions selected for swapping
            print(f"\nSwapping:\n  Student1 at ({class1},{col1},{row1}): {student1}\n  Student2 at ({class2},{col2},{row2}): {student2}")
            '''

            # Swap students in their respective positions
            chromosome[class1].seating[col1][row1], chromosome[class2].seating[col2][row2] = (
                student2,
                student1,
            )
        '''      
        # Debug: Log all students after mutation
        print("\nAfter Mutation:")
        for class_idx, classroom in enumerate(chromosome):
            for col_idx, column in enumerate(classroom.seating):
                for row_idx, student in enumerate(column):
                    print(f"Classroom {class_idx}, Seat ({col_idx},{row_idx}): {student}")
        '''

        return chromosome


    
    def evolve(self, generations=10000, elite_count=10, mutation_rate=0.2):
        """
        Perform the genetic algorithm's iterative evolution.

        Args:
            generations (int): Number of generations to evolve.
            elite_count (int): Number of top chromosomes to carry forward to the next generation.
            mutation_rate (float): Probability of applying mutation to offspring.

        Returns:
            list[Classroom]: The best chromosome found after evolution.
        """
        
        # Generate initial population
        self.generate_initial_population()

        prev_fitness_scores = [self.calculate_fitness(chromosome) for chromosome in self.population]

        for generation in range(generations):
            print(f"Generation {generation + 1}")

            # Calculate fitness for the population
            fitness_scores = [self.calculate_fitness(chromosome) for chromosome in self.population]

            # Select the best chromosomes for elitism
            elite_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:elite_count]
            elite_chromosomes = [self.population[i] for i in elite_indices]

            # Perform roulette wheel selection
            selected_parents = self.roulette_wheel_selection(fitness_scores, num_selected=len(self.population) - elite_count)

            # Generate offspring via crossover
            offspring = []
            for i in range(0, len(selected_parents) - 1, 2):
                parent1 = selected_parents[i]
                parent2 = selected_parents[i + 1]
                child1, child2 = self.one_point_crossover(parent1, parent2)
                offspring.extend([child1, child2])

            # Apply mutation
            for i in range(len(offspring)):
                if random.random() < mutation_rate:
                    offspring[i] = self.multiple_swaps_mutation(offspring[i])

            # Combine elite chromosomes and offspring
            self.population = elite_chromosomes + offspring[: len(self.population) - elite_count]

            # Return the best chromosome after the final generation
            fitness_scores = [self.calculate_fitness(chromosome) for chromosome in self.population]
            best_index = fitness_scores.index(max(fitness_scores))
            # Check for convergence
            if generation > 0 and max(fitness_scores) == max(prev_fitness_scores):
                convergence_count += 1
            else:
                convergence_count = 0

            if convergence_count >= 50:  # Stop if no improvement for 50 generations
                print(f"Converged after {generation + 1} generations.")
                break

            prev_fitness_scores = fitness_scores

        return self.population[best_index]
        





def main():
    # Create some sample students
    students = [
        Student("S1", "CS", "A", "Math"),
        Student("S2", "CS", "A", "Math"),
        Student("S3", "CS", "B", "Math"),
        Student("S4", "EE", "A", "Physics"),
        Student("S5", "EE", "B", "Physics"),
        Student("S6", "EE", "B", "Physics"),
        Student("S7", "DS", "C", "Math"),
        Student("S8", "DS", "C", "Math"),
        Student("S9", "DS", "C", "Math"),
        Student("S10", "EE", "A", "Physics"),
        Student("S11", "EE", "A", "Physics"),
        Student("S12", "EE", "C", "Physics"),
        Student("S13", "CS", "A", "Math"),
        Student("S14", "CS", "B", "Math"),
        Student("S15", "CS", "B", "Math"),
        Student("S16", "EE", "A", "Physics"),
        Student("S17", "EE", "A", "Physics"),
        Student("S18", "EE", "A", "Physics"),
        Student("S19", "DS", "C", "Math"),
        Student("S20", "DS", "C", "Math"),
        Student("S21", "DS", "C", "Math"),
        Student("S22", "EE", "B", "Physics"),
        Student("S23", "EE", "B", "Physics"),
        
    ]
    
    # Create some sample classrooms
    classrooms = [
        Classroom("Room1", 4, 3),
        Classroom("Room2", 4, 3)
    ]
    
    # Initialize the genetic algorithm with students and classrooms
    ga = GeneticAlgorithm(students, classrooms)
    
    # Generate the initial population
    chromosome = ga.evolve(generations=10000)
    
    arr = [chromosome]
    for chromosome in arr:
        for classroom in chromosome:
            print(f"Classroom: {classroom.name}")
            for col, column in enumerate(classroom.seating):
                for row, student in enumerate(column):
                    print(f"Seat: ({col}, {row}), Student: {student}")

if __name__ == "__main__":
    main()


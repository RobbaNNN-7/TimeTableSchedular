from collections import defaultdict, deque
from typing import List
from classes.Student import *
from classes.Classroom import *
import random

class GeneticAlgorithm:
    

    def __init__(self, students: List[Student], classrooms: List[Classroom]):
        self.PopulationCount = 100
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
        probabilities = [score / total_fitness for score in fitness_scores]
        
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
    
    @staticmethod
    def one_point_crossover(parent1, parent2):
        """
        Perform one-point crossover between two parent chromosomes by swapping students 
        between classrooms, ensuring no student repetition.
        
        Args:
            parent1 (list): The first parent chromosome (list of Classroom objects).
            parent2 (list): The second parent chromosome (list of Classroom objects).
        
        Returns:
            tuple: Two offspring chromosomes.
        """
        assert len(parent1) == len(parent2), "Chromosomes must be of the same length"

        # Swap the students in the chosen classroom and column between parent1 and parent2
        offspring1 = [classroom for classroom in parent1]  # Copy of parent1
        offspring2 = [classroom for classroom in parent2]  # Copy of parent2
        
        # Check and fix for student repetition after crossover
        def fix_repetition(offspring):
            seen_students = set()
            for classroom in offspring:
                for column in classroom.seating:
                    for idx, student in enumerate(column):
                        if student != "" and student.student_id in seen_students:
                            # Reassign student to another available spot in the same classroom
                            for other_column in classroom.seating:
                                if "" in other_column:
                                    # Find the first empty seat and reassign the student
                                    other_column[other_column.index("")] = student
                                    column[idx] = ""  # Remove student from previous seat
                                    seen_students.add(student.student_id)
                                    break
                        elif student != "":
                            seen_students.add(student.student_id)
            return offspring
        
        
        # Choose a random crossover point (classroom and column)
        crossover_classroom_index = random.randint(0, len(parent1) - 1)
        crossover_column_index = random.randint(0, parent1[crossover_classroom_index].num_columns - 1)
        
        
        # Swap students in the selected crossover classroom and column
        temp = offspring1[crossover_classroom_index].seating[crossover_column_index]
        offspring1[crossover_classroom_index].seating[crossover_column_index] = parent2[crossover_classroom_index].seating[crossover_column_index]
        offspring2[crossover_classroom_index].seating[crossover_column_index] = temp

        # Fix repetition issues in both offspring
        offspring1 = fix_repetition(offspring1)
        offspring2 = fix_repetition(offspring2)
    
    

    
        return offspring1, offspring2







def main():
    # Create some sample students
    students = [
        Student("S1", "CS", "A", "Math"),
        Student("S2", "CS", "A", "Math"),
        Student("S3", "CS", "B", "Physics"),
        Student("S4", "EE", "A", "Math"),
        Student("S5", "EE", "B", "Physics")
    ]
    
    # Create some sample classrooms
    classrooms = [
        Classroom("Room1", 2, 2),
        Classroom("Room2", 2, 2)
    ]
    
    # Initialize the genetic algorithm with students and classrooms
    ga = GeneticAlgorithm(students, classrooms)
    
    # Generate the initial population
    ga.generate_initial_population()
    
    # Print the generated population
    selected=(ga.roulette_wheel_selection([ga.calculate_fitness(chromosome) for chromosome in ga.population], 5))

    for chromosome in selected[0:2]:
        print(ga.calculate_fitness(chromosome))
        for classroom in chromosome:
            print(f"Classroom: {classroom.name}")
            for col, column in enumerate(classroom.seating):
                for row, student in enumerate(column):
                    print(f"Seat: ({col}, {row}), Student: {student}")

    # Perform one-point crossover between two selected chromosomes
    offspring1, offspring2 = ga.one_point_crossover(selected[0], selected[1])
    arr=[offspring1,offspring2]
    for chromosome in arr:
        print(ga.calculate_fitness(chromosome))
        for classroom in chromosome:
            print(f"Classroom: {classroom.name}")
            for col, column in enumerate(classroom.seating):
                for row, student in enumerate(column):
                    print(f"Seat: ({col}, {row}), Student: {student}")

if __name__ == "__main__":
    main()


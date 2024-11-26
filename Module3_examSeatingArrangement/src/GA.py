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
        Perform one-point crossover at the student level.

        Args:
            parent1 (list[Classroom]): The first parent chromosome (list of Classroom objects).
            parent2 (list[Classroom]): The second parent chromosome (list of Classroom objects).

        Returns:
            tuple: Two offspring chromosomes (lists of Classroom objects).
        """
        # Ensure both parents have the same number of classrooms
        assert len(parent1) == len(parent2), "Parent chromosomes must have the same number of classrooms"

        # Choose random crossover points
        crossover_point_class = random.randint(0, len(parent1) - 1)
        crossover_point_column = random.randint(0, parent2[crossover_point_class].num_columns - 1)
        crossover_point_student = random.randint(0, parent2[crossover_point_class].seats_per_column - 1)

        # Create offspring1 based on parent2 up to crossover point
        offspring1 = [Classroom(c.name, c.num_columns, c.seats_per_column) for c in parent2]

        for i in range(crossover_point_class + 1):
            if i < crossover_point_class:
                # Copy all classrooms before the crossover class from parent2
                offspring1[i] = parent2[i]
            elif i == crossover_point_class:
                # For the crossover class, copy columns up to the crossover column
                for j in range(crossover_point_column + 1):
                    if j < crossover_point_column:
                        offspring1[i].seating[j]=parent2[i].seating[j]
                    else:
                        # For the crossover column, copy students up to the crossover student
                        for k in range(crossover_point_student + 1):
                            offspring1[i].assign_student(j,parent2[i].seating[j][k] )

       
        # Add remaining students from parent1 to offspring1
        for i in range(len(parent1)):
            # Assign unadded students column by column
            for j in range(parent1[i].num_columns):
                for student in parent1[i].seating[j]:
                    # Check if the student is already in offspring1
                    if not any(
                        student.equals(other_student)
                        for classroom in offspring1
                        for col in classroom.seating
                        for other_student in col
                    ):
                        # Find the first available column in the current classroom
                        for class_no in range(len(offspring1)):
                            found = False
                            for col in range(offspring1[class_no].num_columns):
                                if offspring1[class_no].is_seat_available(col):
                                    offspring1[class_no].assign_student(col, student)
                                    found = True
                                    break
                            if found:
                                break

        

        # Create offspring2 based on parent1 up to crossover point
        offspring2 = [Classroom(c.name, c.num_columns, c.seats_per_column) for c in parent1]

        for i in range(crossover_point_class + 1):
            if i < crossover_point_class:
                # Copy all classrooms before the crossover class from parent1
                offspring2[i] = parent1[i]
            elif i == crossover_point_class:
            # For the crossover class, copy columns up to the crossover column
                for j in range(crossover_point_column + 1):
                    if j < crossover_point_column:
                        offspring2[i].seating[j] = parent1[i].seating[j]
                    else:
                        # For the crossover column, copy students up to the crossover student
                        for k in range(crossover_point_student + 1):
                            offspring2[i].assign_student(j, parent1[i].seating[j][k])

        # Add remaining students from parent2 to offspring2
        for i in range(len(parent2)):
            # Assign unadded students column by column
            for j in range(parent2[i].num_columns):
                for student in parent2[i].seating[j]:
                    # Check if the student is already in offspring2
                    if not any(
                    student.equals(other_student)
                    for classroom in offspring2
                    for col in classroom.seating
                    for other_student in col
                    ):
                        # Find the first available column in the current classroom
                        for class_no in range(len(offspring2)):
                            found = False
                            for col in range(offspring2[class_no].num_columns):
                                if offspring2[class_no].is_seat_available(col):
                                    offspring2[class_no].assign_student(col, student)
                                    found = True
                                    break
                            if found:
                                break
    
        return offspring1, offspring2

                    
        
        



def main():
    # Create some sample students
    students = [
        Student("S1", "CS", "A", "Math"),
        Student("S2", "CS", "A", "Math"),
        Student("S3", "CS", "B", "Physics"),
        Student("S4", "EE", "A", "Math"),
        Student("S5", "EE", "B", "Physics"),
        Student("S6", "EE", "B", "Physics"),
        Student("S7", "DS", "C", "Chemistry"),
        Student("S8", "DS", "C", "Chemistry"),
        Student("S9", "DS", "C", "Chemistry"),
        Student("S10", "CS", "A", "Math"),
    ]
    
    # Create some sample classrooms
    classrooms = [
        Classroom("Room1", 2, 2),
        Classroom("Room2", 2, 2),
        Classroom("Room3", 2, 2),
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


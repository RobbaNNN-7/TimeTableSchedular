import json
from datetime import datetime   

class Individual:
    def __init__(self,chromosome):
        self.chromosome=chromosome
        self.fitness = self.calcFitness()

    def extractSchedule(self):
        # Create a dictionary to store dates and times by batch and department
        batch_department_schedule = {}

        for key, value in self.chromosome.items():
            parts = key.split("_")  # Split the key by underscore
            batch = parts[0]        # First part is the batch
            department = parts[1]   # Second part is the department
            
            # Create a key for batch and department
            batch_department_key = (batch, department)
            
            # Extract date and timeslot
            date_object = datetime.strptime(value["date"], "%Y-%m-%d")
            day = date_object.strftime("%A")
            date_time = {"date": value["date"], "timeslot": value["timeslot"],"day":day}
            
            # Append to the dictionary
            if batch_department_key not in batch_department_schedule:
                batch_department_schedule[batch_department_key] = []
            batch_department_schedule[batch_department_key].append(date_time)

        # Print the result
        #for key, times in batch_department_schedule.items():
            #print(f"Batch: {key[0]}, Department: {key[1]}, Dates and Times: {times}")

        return batch_department_schedule

    def calcFitness(self):
        fitnessScore=1000
        schedule=self.extractSchedule()
        
        # Iterate over each batch and department
        for (batch, department), exams in schedule.items():
            
            # Extract all dates for the current department
            dates = [exam['date'] for exam in exams]
            days=[(exam['day'],exam['timeslot']) for exam in exams]

            for (day,timeslot) in days:
                if day=="Friday" and timeslot=="2-4": # If exam on Friday 2-4 slot decrease fitnessScore
                    fitnessScore-=30

                if day=="Saturday": #If exam on Saturday decrease fitnessScore
                    fitnessScore=-50
                    

            # Compare each date with the others in the list
            for i, date1 in enumerate(dates):
                for j, date2 in enumerate(dates):
                    if i != j:  # Skip comparing the same exam with itself
                        if date1 == date2: #If there are 2 exams in a day decrease fitnessScore
                            fitnessScore-=40
        return fitnessScore



        
                

                    
                
            
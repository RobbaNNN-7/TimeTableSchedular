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
        fitnessScore = 1000
        schedule = self.extractSchedule()
        
        # Track exams by batch+department+date+timeslot combination
        batch_dept_schedule = {}
        
        # Iterate over each batch and department
        for (batch, department), exams in schedule.items():
            key = f"{batch}_{department}"
            if key not in batch_dept_schedule:
                batch_dept_schedule[key] = {}
                
            # Count exams per date and timeslot for this batch+department
            for exam in exams:
                date = exam['date']
                timeslot = exam['timeslot']
                schedule_key = f"{date}_{timeslot}"
                
                if schedule_key not in batch_dept_schedule[key]:
                    batch_dept_schedule[key][schedule_key] = 0
                batch_dept_schedule[key][schedule_key] += 1
                
                # # Make same-time constraint violation extremely costly (-1000)
                # if batch_dept_schedule[key][schedule_key] > 1:
                #     fitnessScore -= float("-inf")  # Increased from -500 to -1000
                    
                # Significant penalty (-300) for same batch+dept having multiple exams on same day
                same_day_exams = sum(1 for k, v in batch_dept_schedule[key].items() 
                                if k.split('_')[0] == date)
                if same_day_exams > 1:
                    fitnessScore -= 300  # Increased from -200 to -300
                
                # Normal penalties
                if exam['day'] == "Friday" and exam['timeslot'] == "2-4":
                    fitnessScore -= 30
                if exam['day'] == "Saturday":
                    fitnessScore -= 50
                    
        return fitnessScore



        
                

                    
                
            
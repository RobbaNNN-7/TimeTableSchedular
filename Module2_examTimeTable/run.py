from src.genetic import *
from src.csp import *

def generate_schedule_with_timeslots(schedule,subjects):
    # Initialize the result structure to match the input JSON format
    subjectsTimeSlots={}
    for key, value in schedule.items():
        subjectsTimeSlots[key]=[value["timeslot"],value["date"]]

    for subject in subjects:
        subject["sections"] = ', '.join(subject["sections"])
        key=subject["batch"]+"_"+subject["department"]+"_"+subject["name"]
        subject["date"]=subjectsTimeSlots[key][1]
        subject["timeslot"]=subjectsTimeSlots[key][0]
        

    return subjects

def print_schedule(schedule):
    """Print schedule in a formatted way, handling both CSP and GA output formats"""
    if isinstance(schedule, dict):
        # Handle CSP output format
        print("Schedule Format:")
        for key, value in schedule.items():
            batch, dept, subject = key.split('_')
            print(f"Subject: {subject}")
            print(f"Batch: {batch}")
            print(f"Department: {dept}")
            print(f"Date: {value['date']}")
            print(f"Timeslot: {value['timeslot']}")
            print("-" * 50)
    else:
        # Handle GA output format (list of dictionaries)
        df = pd.DataFrame(schedule)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by=['date', 'timeslot'])
        df.columns = ['Course', 'Batch', 'Department', 'Sections', 'Instructor', 'Date', 'Timeslot']
        print(df.to_string(index=False))

# Example Usage
def main():
    filename = "input.json"  # Modify with your actual JSON file path
    with open(filename, 'r') as file:
        data = json.load(file)

    start_date = datetime.strptime(data["startDate"], "%Y-%m-%d")
    end_date = datetime.strptime(data["endDate"], "%Y-%m-%d")
    timeslots = generate_valid_timeslots(start_date, end_date)
    
    schedule = solve_csp(data['subjects'], data['batchSections'], timeslots)
    if schedule is None:
        print("No valid schedule possible. Please check constraints.")
        return
    print("Schedule generated by CSP:")
    print_schedule(schedule)
    ga = GeneticAlgorithm(schedule,data["startDate"],data["endDate"])
    best_schedule = ga.run()
  # Print the best schedule
    print("Best exam schedule generated by Genetic Algorithm:")
    print_schedule(best_schedule)
    best_schedule=generate_schedule_with_timeslots(best_schedule,data['subjects'])
    # Export the best schedule to an Excel file
    df = pd.DataFrame(best_schedule)
    # Convert 'date' to datetime format for proper sorting
    df['date'] = pd.to_datetime(df['date'])

    # Format the 'date' column to YYYY-MM-DD (remove time part)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    # Sort by 'date' first and then by 'timeslot'
    df = df.sort_values(by=['date', 'timeslot'])
    df.columns = ['Course', 'Batch', 'Department','Sections','Instructor','Date','Timeslot']
    df.to_excel("best_exam_schedule.xlsx", index=False)
    print("Best exam schedule exported to 'best_exam_schedule.xlsx'.")


if __name__ == '__main__':
    main()
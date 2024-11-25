from genetic import *

def generate_schedule_with_timeslots(schedule,subjects):
    # Initialize the result structure to match the input JSON format
    subjectsTimeSlots={}
    for key, value in schedule.items():
        parts = key.split("_")  # Split the key by underscore
        subject=parts[2]
        subjectsTimeSlots[subject]=[value["timeslot"],value["date"]]

    for subject in subjects:
        subject["sections"] = ', '.join(subject["sections"])
        subject["date"]=subjectsTimeSlots[subject["name"]][1]
        subject["timeslot"]=subjectsTimeSlots[subject["name"]][0]
        

    return subjects


# Example Usage
def main():
    filename = "input.json"  # Modify with your actual JSON file path
    with open(filename, 'r') as file:
        data = json.load(file)

    start_date = datetime.strptime(data["startDate"], "%Y-%m-%d")
    end_date = datetime.strptime(data["endDate"], "%Y-%m-%d")
    timeslots = generate_valid_timeslots(start_date, end_date)
    
    schedule = solve_csp(data['subjects'], data['batchSections'], timeslots)
    ga = GeneticAlgorithm(schedule)
    best_schedule = ga.run()
    best_schedule=generate_schedule_with_timeslots(best_schedule,data['subjects'])
        

    # Print the best schedule
    print(json.dumps(best_schedule, indent=4))

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
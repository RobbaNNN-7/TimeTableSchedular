class Classroom:
    def __init__(self, name: str, num_columns: int, seats_per_column: int):
        self.name = name
        self.num_columns = num_columns
        self.seats_per_column = seats_per_column
        # Initialize seating as a list of columns, where each column is a list of seats
        self.seating = [[] for _ in range(num_columns)]
    
    def is_seat_available(self, column: int) -> bool:
        """Check if there is space available in a given column."""
        return len(self.seating[column]) < self.seats_per_column
    
    def assign_student(self, column: int, student_id: str):
        """Assign a student to a column if there is space."""
        if self.is_seat_available(column):
            self.seating[column].append(student_id)
        else:
            raise ValueError(f"Column {column} is full in classroom {self.name}.")
    
    def to_dict(self):
        return {
            "name": self.name,
            "num_columns": self.num_columns,
            "seats_per_column": self.seats_per_column,
            "seating": [[student.to_dict() for student in column] for column in self.seating],
        }
class Classroom:
    def __init__(self, name: str, num_columns: int, seats_per_column: int):
        self.name = name
        self.num_columns = num_columns
        self.seats_per_column = seats_per_column
        self.seating = [["" for _ in range(num_columns)] for _ in range(seats_per_column)]

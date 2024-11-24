class Section:
    def __init__(self, name, course):
        self.name = name
        self.course = course
        
    def __str__(self):
        return f"{self.course.name} - {self.name}"
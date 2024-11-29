class Student:
    def __init__(self, student_id: str, department: str, section: str, subject: str):
        self.student_id = student_id
        self.department = department
        self.section = section
        self.subject = subject
    
    def __str__(self):
        """Readable representation of a student."""
        return f"ID: {self.student_id}, Dept: {self.department}, Section: {self.section}, Subject: {self.subject}"

class Student:
    def __init__(self,studentID,coursesEnrolled):
        self.studentID = studentID
        self.coursesEnrolled = []
    
    def enroll_course(self,course):
        self.coursesEnrolled.append(course)


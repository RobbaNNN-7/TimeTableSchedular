import course

class coures:
    def __init__(self,courses):
        self.courses = []

    def add_course(self,course):
        self.courses.add(course)

    def display_courses(self):
        if not self.course:
            return
        else:
            for crc in self.courses:
                course.display_course_info()


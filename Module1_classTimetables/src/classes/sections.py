import course

class Section:
    def __init__(self, section_name, course_list):
        self.section_name = section_name
        self.course_list = course_list  
        self.timetable = {}  # Dictionary to store the timetable for this section (course -> (time_slot, room, instructor))

    def assign_course_to_slot(self, course, time_slot, room, instructor):
        self.timetable[course.name] = (time_slot, room, instructor)

    def get_timetable(self):
        return self.timetable
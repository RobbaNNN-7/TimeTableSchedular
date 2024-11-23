from typing import List, Dict, Tuple
import random
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Border, Side, Alignment, Font
from openpyxl.utils import get_column_letter

class TimeTableCSP:
    def __init__(self):
        self.sections = ['CSE-A', 'CSE-B', 'CSE-C', 'CSE-D', 'CSE-E']
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.hours_per_day = 8
        self.break_hour = 4  # 5th hour (0-based index is 4)
        
        # Courses with format: {name: {'theory': hours, 'lab': hours}}
        self.courses = {
            'Data Structures': {'theory': 3, 'lab': 3},
            'Programming': {'theory': 3, 'lab': 3},
            'Algorithms': {'theory': 3, 'lab': 0},
            'Database': {'theory': 3, 'lab': 3},
            'Networks': {'theory': 2, 'lab': 0},
            'Operating Systems': {'theory': 2, 'lab': 3}
        }
        
        self.theory_rooms = ['Room101', 'Room102', 'Room103']
        self.lab_rooms = ['Lab101', 'Lab102']
        
        # Initialize empty timetable
        self.timetable = {
            section: {
                day: [None for _ in range(self.hours_per_day)]
                for day in range(len(self.days))
            }
            for section in self.sections
        }
        
        # Set break time for all sections
        self._set_break_time()

    def _set_break_time(self):
        """Set break time for all sections on all days"""
        for section in self.sections:
            for day in range(len(self.days)):
                self.timetable[section][day][self.break_hour] = {
                    'course': 'Break',
                    'room': 'Break',
                    'type': 'break'
                }

    def is_slot_free(self, section: str, day: int, hour: int, duration: int = 1) -> bool:
        """Check if a time slot is free for the given duration"""
        if hour + duration > self.hours_per_day:
            return False
            
        # Check if the slot overlaps with break time
        if any(h == self.break_hour for h in range(hour, hour + duration)):
            return False
            
        return all(self.timetable[section][day][h] is None 
                  for h in range(hour, hour + duration))

    def find_free_slot(self, section: str, duration: int = 1) -> Tuple[int, int]:
        """Find a free slot for the given duration"""
        possible_slots = []
        for day in range(len(self.days)):
            for hour in range(self.hours_per_day - duration + 1):
                if self.is_slot_free(section, day, hour, duration):
                    possible_slots.append((day, hour))
        
        return random.choice(possible_slots) if possible_slots else None

    def schedule_session(self, section: str, course: str, is_lab: bool):
        """Schedule a theory or lab session"""
        duration = 3 if is_lab else 1
        room_list = self.lab_rooms if is_lab else self.theory_rooms
        course_name = f"{course} Lab" if is_lab else course
        
        slot = self.find_free_slot(section, duration)
        if not slot:
            return False
        
        day, start_hour = slot
        room = random.choice(room_list)
        
        # Schedule the session
        for hour in range(start_hour, start_hour + duration):
            self.timetable[section][day][hour] = {
                'course': course_name,
                'room': room,
                'type': 'lab' if is_lab else 'theory'
            }
        return True

    def generate_timetable(self):
        for section in self.sections:
            # First schedule labs (as they need 3 consecutive hours)
            for course, hours in self.courses.items():
                if hours['lab'] > 0:
                    if not self.schedule_session(section, course, is_lab=True):
                        return False
            
            # Then schedule theory classes
            for course, hours in self.courses.items():
                for _ in range(hours['theory']):
                    if not self.schedule_session(section, course, is_lab=False):
                        return False
        return True

    def solve(self):
        max_attempts = 100
        for attempt in range(max_attempts):
            # Reset timetable
            self.timetable = {
                section: {
                    day: [None for _ in range(self.hours_per_day)]
                    for day in range(len(self.days))
                }
                for section in self.sections
            }
            
            # Set break time before generating schedule
            self._set_break_time()
            
            if self.generate_timetable():
                return True
        return False

    def export_to_excel(self, filename: str = 'timetable.xlsx'):
        wb = Workbook()
        
        # Styles
        header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
        theory_fill = PatternFill(start_color="E6F3FF", end_color="E6F3FF", fill_type="solid")
        lab_fill = PatternFill(start_color="FFE6E6", end_color="FFE6E6", fill_type="solid")
        break_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
        border = Border(left=Side(style='thin'), right=Side(style='thin'),
                       top=Side(style='thin'), bottom=Side(style='thin'))
        center_aligned = Alignment(horizontal='center', vertical='center', wrap_text=True)
        header_font = Font(bold=True)
        
        for section in self.sections:
            if section == self.sections[0]:
                ws = wb.active
                ws.title = section
            else:
                ws = wb.create_sheet(section)
            
            # Set column widths
            ws.column_dimensions['A'].width = 10
            for i in range(len(self.days)):
                col = get_column_letter(i + 2)
                ws.column_dimensions[col].width = 20
            
            # Write section name
            ws.merge_cells('A1:F1')
            cell = ws['A1']
            cell.value = f"Timetable for {section}"
            cell.fill = header_fill
            cell.font = Font(bold=True, size=14)
            cell.alignment = center_aligned
            cell.border = border
            
            # Write days
            for day_idx, day in enumerate(self.days):
                cell = ws.cell(row=2, column=day_idx + 2)
                cell.value = day
                cell.fill = header_fill
                cell.font = header_font
                cell.border = border
                cell.alignment = center_aligned
            
            # Write hours
            for hour in range(self.hours_per_day):
                cell = ws.cell(row=hour + 3, column=1)
                cell.value = f"Hour {hour + 1}"
                cell.fill = header_fill
                cell.font = header_font
                cell.border = border
                cell.alignment = center_aligned
            
            # Fill in the schedule
            for day in range(len(self.days)):
                for hour in range(self.hours_per_day):
                    cell = ws.cell(row=hour + 3, column=day + 2)
                    slot = self.timetable[section][day][hour]
                    
                    if slot:
                        cell.value = f"{slot['course']}\n{slot['room']}"
                        if slot['type'] == 'break':
                            cell.fill = break_fill
                        elif slot['type'] == 'lab':
                            cell.fill = lab_fill
                        else:
                            cell.fill = theory_fill
                    else:
                        cell.value = "---"
                    
                    cell.border = border
                    cell.alignment = center_aligned
            
            # Set row heights
            ws.row_dimensions[1].height = 30
            for row in range(3, 11):
                ws.row_dimensions[row].height = 60
        
        wb.save(filename)
        print(f"Timetable has been exported to {filename}")

scheduler = TimeTableCSP()
if scheduler.solve():
    scheduler.export_to_excel("optimized_timetable.xlsx")
    print("Timetable generated successfully!")
else:
    print("Could not generate a valid timetable after maximum attempts.")
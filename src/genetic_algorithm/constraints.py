"""
Constraints

Hard Constraints:
- No  student  group  has  two  events at  the same time. 
- No  lecturer  has  two events  at the  same time.
- No  event is in  a room with less capacity than the number of students at the event.

Soft Constraints:
- Technical courses must be before break.

Rooms: A list of rooms and their capacities.
Time Slots: Represent the 5x7 timetable as 5 rows (days) x 7 columns (time slots).
Example: courses = [{"name": "Math", "type": "technical", "hours": 3}, ...].

timetable = [
    ['slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6', 'slot7'],  # Day 1 -> Monday
    ['slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6', 'slot7'],  # Day 2 -> Tuesday
    ['slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6', 'slot7'],  # Day 3 -> Wednesday
    ['slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6', 'slot7'],  # Day 4 -> Thrusday
    ['slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6', 'slot7'],  # Day 5 -> Friday
]

Each slot can store a tuple: (course, instructor, room).




"""
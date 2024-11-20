from helper_methods import validate_time_slot

class instructor:
    def __init__(self,id,availibility):
        self.id = id
        self.availibility = [True] * 7
        
    def is_availible(self,time_slot):
        validate_time_slot(time_slot)
        return self.availibility[time_slot]

    def assign_course(self,time_slot):
        validate_time_slot(time_slot)
        self.availibility[time_slot] = False # Mark Time Slot as False
    
    def remove_course(self,time_slot):
        validate_time_slot(time_slot)
        self.availibility[time_slot] = True # Mark Time Slot As True


    
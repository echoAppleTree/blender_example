

class Call_Back_Event():

    def __init__(self):

        self.db = None

        self.func = None
        self.positive_args = None
        self.negative_args = None
        self.scrollable = False
        self.shift_func = None
        self.shift_arges = None

    
    def event(self):

        try:
            if self.db.event.shift_pressed and self.shift_func:
                if self.shift_arges:
                    self.shift_func(*self.shift_arges)
                else:
                    self.shift_func()

            elif self.func != None:

                if self.db.event.alt_left_clicked:
                    if self.negative_args != None:
                        self.func(*self.negative_args)
                
                elif self.positive_args != None:
                    self.func(*self.positive_args)

                else:
                    self.func()

        except:
            pass


    def external_cell_event_call(self, positive=True):
        '''Used for scrolling, the cells event will call this not self.'''

        if self.scrollable:

            if self.func != None:

                if self.db.event.alt_left_clicked:
                    if self.negative_args != None:
                        self.func(*self.negative_args)
                
                elif self.positive_args != None:
                    self.func(*self.positive_args)

                else:
                    self.func()
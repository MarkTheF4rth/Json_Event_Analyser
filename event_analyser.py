'''
Iterate through formatted events and return any significant information
'''

import os
import json

# How many times an event needs to show up to be significant
SIGNIFICANT_EVENT_CUTOFF = 1000

class Event_Analyser:
    def __init__(self, event_dir):
        self.event_dir = event_dir
        self.events = os.listdir(event_dir)
        self.significant_events = []


    def get_significant_events(self):
        ''' Iterate over events, add any event that occurs more than a set amount
            of times to significant events'''
        print('%i unique events found' %(len(self.events)))
        for event in self.events:
            event_contents = json.load(open(os.path.join(self.event_dir, event), 'r'))
            if len(event_contents['time']) >= SIGNIFICANT_EVENT_CUTOFF:
                self.significant_events.append(event)

    def analyse_significant_events(self):
        ''' For every significant event, see what preceding events were more common
            display in terms of percentages'''
        for event in self.significant_events:
            related_events = {} # related events : how many times they were found
            event_counter = 0
            event_contents = json.load(open(os.path.join(self.event_dir, event), 'r'))
            for event_instance in event_contents['time'].values():
                for related_event in event_instance.values():
                   
                    if related_event not in related_events:
                        related_events[related_event] = 0
                    related_events[related_event] += 1
                event_counter += 1
            
            print(event, event_counter)
            for related_event, occurunces in related_events.items():
                if (occurunces//event_counter > 0.50):
                    print(related_event, occurunces)

            print('\n')


if __name__ == "__main__":
    e_anal = Event_Analyser('formattedEvents')
    e_anal.get_significant_events()
    e_anal.analyse_significant_events()

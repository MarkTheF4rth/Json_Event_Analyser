'''
Iterates through events, format it as part of our current make-shift DB
'''

import os
import json
import receive

# Template for the event json
EVENT_JSON_TEMPLATE = {
'time':{}}

# Time in seconds after which an event is inconsequential to the next one
SIGNIFICANT_TIME = 600

# The format of the event name, based on the keys in the json
EVENT_FORMAT = [
'node',
'event',
'level']

# If these keys are present, add them to the name of the event
SUPPLEMENTARY_FORMAT = [
'element',
'state']

class Feeder(receive.Consumer):
    '''Runs through files in a given dir'''
    def __init__(self, output_dir):
        self.current_events = {} # events that are classed as relevant
        self.output_dir = output_dir
        super().__init__('event')

    def callback(self, ch, method, properties, body):
        '''when receiving an event, deal with it'''
        event = json.loads(body)
        time = event['time']
        event_name = self.format_event_name(event)

        self.correct_for_time(time)
        self.current_events[time] = event_name
        self.append_event(event_name, time)
        print('received event', event_name)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def iterate_over_files(self, input_dir):
        '''Iterate over every file in the input dir
           if its a unique event, add it'''
        for json_file in sorted(os.listdir(input_dir)):
            # assume all given files are properly formatted for now
            time, event_id = json_file.split('|')
            event_contents = json.load(open(os.path.join(input_dir, json_file), 'r'))
            event_name = self.format_event_name(event_contents)

            self.correct_for_time(time)
            self.current_events[time] = event_name
            self.append_event(event_name, time)

    def format_event_name(self, event_contents):
        '''Create the name of the event'''
        section_1 = []
        section_2 = []
        for element in EVENT_FORMAT:
            section_1.append(self.sanitise_string(event_contents[element]))

        if all([x in event_contents for x in SUPPLEMENTARY_FORMAT]):
            for element in SUPPLEMENTARY_FORMAT:
                section_2.append(self.sanitise_string(event_contents[element]))

        section_1 = '_'.join(section_1)
        section_2 = '_'.join(section_2)
        return '|'.join([section_1, section_2])


    def correct_for_time(self, new_time):
        '''Remove events in self.current_events which are classed to have happened
           too long ago to be important'''
        self.current_events = {time:event_name for time, event_name in self.current_events.items()
                               if (float(new_time) - float(time) < SIGNIFICANT_TIME)}


    def append_event(self, event_name, event_time):
        '''Add this instance of a given event to its corresponding json
           If the json doesn't exist, create one'''
        event_path = os.path.join(self.output_dir, event_name+'.json')
        if not os.path.exists(event_path):
            # create a json if one doesn't exist already
            with open(event_path, 'w') as new_event_file:
                new_event_file.write(json.dumps(EVENT_JSON_TEMPLATE))

        with open(event_path, 'r') as event_file:
            past_events = json.load(event_file)

        past_events['time'].update({event_time:self.current_events})
        with open(event_path, 'w') as event_file:
            event_file.write(json.dumps(past_events))


    def sanitise_string(self, string):
        '''Replaces annoying characters with .'s'''
        chars = ['/', ' ']
        for char in chars:
            string = string.replace(char, '.')
        return string


if __name__ == "__main__":
    testdir = 'timeorderedringdumptest'
    outputdir = 'formattedEvents'
    feeder = Feeder(outputdir)

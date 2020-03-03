'''
splits ringdump.json, naming them by their unix time followed by their hash
I know this was done, but the other one isn`t sorted by time
'''
import os
import json

def splitter(json_file, write_dir, limit):
    counter = 0
    for line in open(json_file, 'r'):
        x = json.loads(line)
        print(x)
        name = str(x['time'])+'|'+x['_id']['$oid']+'.json'
        with open(os.path.join(write_dir, name), 'w') as new_file:
            new_file.write(line)
        counter += 1
        if counter > limit:
            break

splitter('ringdump-with-elements.json', 'timeorderedringdumptest', 100000)

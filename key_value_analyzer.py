import os
import json
import itertools

class colprint:
    '''prints a string in a defined colour when invoked'''
    def __init__(self):
        self.empty = ''
        self.okblue = '\033[94m' # end statement
        self.green = '\033[92m' # confirmation
        self.lightred = '\033[93m' # unreliable tag
        self.cyan = '\033[36m' # 
        self.yellow = '\033[33m' # 
        self.magenta = '\033[35m' # 
        self.fail = '\033[91m'    # content has only been seen once
        self.header = '\033[95m'  #   |
        self.bold = '\033[1m'     #   |
        self.underline = '\033[4m'#   |

        self.endc = '\033[0m' # applied to end of string

    def wrap(self, string, colour='empty'):
        return (getattr(self, colour) + string + self.endc)

    def __call__(self, string, colour='empty'):
        print(self.wrap(string, colour))


class KeyAnalyser:
    '''Finds common keys in lots of json files, lists common values'''
    def __init__(self, target_dir):
        self.errors = [] # json files which couldn't be decoded
        self.key_counter = {} # track how many times keys come up, helps to know if a key is expected
        self.file_counter = 0 # how many files have been scanned
        self.key_list = {} # stores all found keys, and a set of their possible values

        self.description_cutoff = 50 # percentage of unique values to be considered a description
        self.name_cutoff = 20 # how many unique values constitute a name rather than a value

        self.iterate_over_dir(target_dir)


    def iterate_over_dir(self, target_dir):
        '''iterate over given directory and run the reader on them'''

        for potential in os.listdir(target_dir):
            if potential.endswith('.json'):
                try:
                    self.reader(json.load(open(os.path.join(target_dir, potential))))
                    self.file_counter += 1
                except json.decoder.JSONDecodeError:
                    self.errors.append(potential)


    def reader(self, json):
        '''reads the json file, adds any new keys and files to the list
        NOTES: some keys may be defined outside of target files'''

        for key, value  in json.items():
            if key not in self.key_list:
                if type(value) == dict: # messy code to deal with a single item stored in a dict
                    value = next(itertools.islice(value.values(), 0, None)) # get the first value
                    continue
                print(value)
                self.key_list[key] = set([value])
                self.key_counter[key] = 0
                continue
    
            self.key_list[key].add(value)
            self.key_counter[key] += 1


    def print_analysis(self):
        '''prints findings:
        - keys that show up less than the amount of files are unreliable
        - keys with a similar number of values to the file amount are considered descriptions
        - keys with more than 10 values, but not satisfying previous requirements, are names
        '''

        print_list = []

        for key, values in self.key_list.items():
            col = 'green'
            tag1 = ['reliable' if len(values) == self.file_counter 
                    else 'unreliable(%i/%i)' % (self.key_counter[key], self.file_counter)][0]

            if len(values) > self.file_counter//(100/self.description_cutoff):
                tag2 = 'description'
            elif len(values) > self.name_cutoff:
                tag2 = 'name'
            else:
                tag2 = '{} - {}'.format('value', values)

            if 'unreliable' in tag1:
                col = 'lightred'
                if 'unreliable' in tag1 and self.key_counter[key] == 1:
                    col = 'fail'

            print_list.append([key, tag1, tag2, col])

        for item in sorted(print_list, key = lambda x : x[1]):
            CPRINT('{} | {} | {}'.format(*item[:-1]), item[-1])
            
        CPRINT('%i files scanned, %i failed' % (self.file_counter, len(self.errors)), 'okblue')

    

if __name__ == "__main__":
    CPRINT = colprint()
    key_analyser = KeyAnalyser('timeorderedringdumptest')
    key_analyser.print_analysis()

'''
splits ringdump.json, naming them by their unix time followed by their hash
I know this was done, but the other one isn`t sorted by time
'''
import os
import pika
import time

ROUTING_KEY = 'events'

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=ROUTING_KEY)

def splitter(json_file, write_dir, limit):
    counter = 0
    for line in open(json_file, 'r'):
        counter += 1

        channel.basic_publish(exchange='',
                              routing_key=ROUTING_KEY,
                              body=line,
                              properties = pika.BasicProperties(delivery_mode=2))
        print(line)

        if counter > limit:
            break

        time.sleep(1)


splitter('ringdump-with-elements.json', 'timeorderedringdumptest', 100)
connection.close()

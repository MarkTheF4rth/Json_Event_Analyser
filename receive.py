import pika
import time

class Consumer:
    '''Reads the event message queue'''
    def __init__(self, event_queue_name):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='events')

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='events',
                      on_message_callback=self.callback)

        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        '''Basic callback, made to be overwritten'''
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(body)



if __name__ == "__main__":
    consumer = Consumer('events')
    print('Waiting for messages, exit with ctrl+c')

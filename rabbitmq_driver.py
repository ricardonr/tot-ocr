from typing import Iterator
from queue import Queue
from threading import Thread
import json

from pika import BlockingConnection, ConnectionParameters
from service import NewWorkloadEvent, NewWorkloadStream

class RabbitMqConsumerThread(Thread):
  def __init__(self, host: str, topic: str, callback):
    Thread.__init__(self)
    conn = BlockingConnection(
      ConnectionParameters(host='localhost')
    )
    self.channel = conn.channel()
    self.topic = topic
    self.callback = callback

  def run(self):
    self.channel.exchange_declare(exchange=self.topic, exchange_type='fanout', durable=True)
    result = self.channel.queue_declare(queue='', durable=True)
    queue_name = result.method.queue
    self.channel.queue_bind(exchange=self.topic, queue=queue_name)
    self.channel.basic_consume(
      queue=queue_name,
      on_message_callback=self.callback,
      auto_ack=True
    )
    self.channel.start_consuming()

class RabbitMqNewWorkloadStream(NewWorkloadStream):

  def __init__(self, host: str):
    self.host = host
    self.q = Queue()

  def new_workload(self, topic: str) -> Iterator[NewWorkloadEvent]:
    return self.__new_workload_event_generator(topic)

  def __new_workload_event_generator(self, topic: str):
    consumer_thread = RabbitMqConsumerThread(self.host, topic, self.__message_callback)
    consumer_thread.start()
    while True:
      print('waiting next item')
      next_item = self.q.get(block=True)
      print(next_item)
      yield next_item

  def __message_callback(self, ch, method, properties, body):
    workload_json = json.loads(body)
    workload = NewWorkloadEvent(
      workload_json['ID'],
      workload_json['BucketName'],
      workload_json['ObjectKey'],
    )
    self.q.put(workload)
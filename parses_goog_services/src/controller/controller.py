from ..service.service import Service
from ..config.config import RabbitConf
import pika
import json

class Controller:
    def __init__(self, in_queue_name: str, out_queue_name: str, service: Service, rabbit_config: RabbitConf) -> None:
        self.service = service
        self.in_queue_name = in_queue_name
        self.out_queue_name = out_queue_name
        self.rabbit_config = rabbit_config

    def start_reading(self) -> None:
        self.__connect_to_rabbit()
        while True:
            self.__read_message()

    def prosess_message(self, message: bytes):

        body = message.decode('utf-8')
        message_str = json.loads(body)
        res = self.service.parce(message_str)
        if res != None:
            for el in res:
                self.write_to_rabbit(el)

    def __read_message(self):

        method_frame, header_frame, body = self.chanel.basic_get(queue=self.in_queue_name, auto_ack=False)
        if method_frame:
            self.prosess_message(body)
            self.chanel.basic_ack(method_frame.delivery_tag)
    
    def write_to_rabbit(self, message: str) -> None:

        message_json = json.dumps(message).encode()
        self.chanel.basic_publish(exchange='', routing_key=self.out_queue_name, body=message_json)

    def __connect_to_rabbit(self):

        credentials = pika.PlainCredentials(self.rabbit_config.user, self.rabbit_config.password)
        parameters = pika.ConnectionParameters(self.rabbit_config.host,
                                        self.rabbit_config.port,
                                        self.rabbit_config.way,
                                        credentials)

        self.connection = pika.BlockingConnection(parameters)    
        self.chanel = self.connection.channel()

        self.in_queue = self.__get_queue(self.in_queue_name)
        self.out_queue = self.__get_queue(self.out_queue_name)

    def __get_queue(self, name: str):
        return self.chanel.queue_declare(queue=name, passive=True)

from ..service.service import Service
from ..repository.mysql import Repository
from ..config.config import RabbitConf
import pika
import json

class Controller:
    def __init__(self, in_queue_name: str, service: Service, repository: Repository, rebbit_config: RabbitConf) -> None:
        self.service = service
        self.in_queue_name = in_queue_name
        self.repository = repository
        self.rebbit_config = rebbit_config

    def start_reading(self) -> None:
        try:
            self.__connect_to_rabbit()
            while True:
                self.__read_message()
        finally:
            self.chanel.close()
            self.connection.close()
            print('[[[Controller is stop]]]')

    def prosess_message(self, message: bytes) -> None:

        body = message.decode('utf-8')
        organization = json.loads(body)
        res = self.service.parce(organization)
        self.repository.update_db_site(res.to_map())

    def __read_message(self):
        method_frame, header_frame, body = self.chanel.basic_get(queue=self.in_queue_name, auto_ack=False)
        if method_frame:
            self.prosess_message(body)
            self.chanel.basic_ack(method_frame.delivery_tag)

    def __connect_to_rabbit(self):

        credentials = pika.PlainCredentials(self.rebbit_config.user, self.rebbit_config.password)
        parameters = pika.ConnectionParameters(self.rebbit_config.host,
                                        self.rebbit_config.port,
                                        self.rebbit_config.way,
                                        credentials)

        self.connection = pika.BlockingConnection(parameters)    
        self.chanel = self.connection.channel()
        self.in_queue = self.__get_queue(self.in_queue_name)

    def __get_queue(self, name: str):
        return self.chanel.queue_declare(queue=name, passive=True)

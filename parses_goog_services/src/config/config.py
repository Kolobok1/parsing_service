from dotenv import load_dotenv
import os

class GoogleConf:
    def __init__(self) -> None:
        user_id = os.environ["GOOGLE_USER_ID"],
        self.user_id = user_id[0]
        self.key = os.environ["GOOGLE_KEY"]

class MysqlConf:
    def __init__(self) -> None:
        self.user = os.environ["DB_USER"]
        self.password = os.environ["DB_PASSWORD"]
        self.host = os.environ["DB_HOST"]
        self.port = int(os.environ["DB_PORT"])
        self.database = os.environ["DB_NAME"]

class RabbitConf:
    def __init__(self) -> None:
        self.user = os.environ["RABBIT_USER"]
        self.password = os.environ["RABBIT_PASSWORD"]
        self.host = os.environ["RABBIT_HOST"]
        self.port = int(os.environ["RABBIT_PORT"])
        self.way = os.environ["RABBIT_WAY"]

class Config:
    def __init__(self) -> None:
        if os.environ["ENV"] != "docker":
            load_dotenv()
        google = GoogleConf()
        mysql = MysqlConf()
        rabbit = RabbitConf()

        self.google = google
        self.mysql = mysql
        self.rabbit = rabbit

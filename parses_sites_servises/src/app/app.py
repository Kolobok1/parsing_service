from ..config.config import Config
from ..controller.controller import Controller
from ..repository.mysql import Repository
from ..service.service import Service
import requests

class App:
    def __init__(self, session: requests.Session) -> None:
        config = Config()
        repository = Repository(config.mysql)
        service = Service(session, repository)
        controller = Controller('scraping',service, repository, config.rabbit)

        self.controller = controller

    def run(self) -> None:
        self.controller.start_reading()

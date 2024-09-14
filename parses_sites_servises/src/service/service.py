from ..repository.mysql import Repository
from ..models.models import CompanyInfo
from .parser_site import ParserSite
import requests

class Service:
    def __init__(self, session: requests.Session, repository: Repository) -> CompanyInfo:
        stop_email_list = []
        self.repository = repository
        for i in self.repository.get_stop_email():
            stop_email_list.append(i['email'])
        self.ps = ParserSite(session,stop_email_list)

    def parce(self, organization: dict) -> CompanyInfo:

        data = CompanyInfo()
        data.organization_id = organization['id']
        data.site = organization['site']
        data.confirmation = organization['confirmation']

        data = self.ps.start(data)

        return data

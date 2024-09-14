import requests
import re
from bs4 import BeautifulSoup as bs4
from ..config.config import GoogleConf
from ..repository.mysql import Repository


class Service:
    def __init__(self, session: requests.Session, google_config: GoogleConf, repository: Repository) -> None:
        self.session = session
        self.google_config = google_config
        self.repository = repository

    def check_page(self, url: str) -> bs4:
        self.resp = self.session.get(url=url)
        soup = bs4(self.resp.text, features="lxml")

        return soup

    def check_google_status(self, url: str, inn: str, address: str) -> str:

        address = address.split(None, 1)[1].split(',')
        new_address = ''
        for i in address[:-1]:
            if i.find('д.') != -1:
                new_address += i
                break
            new_address += i + ','

        new_url = f'http://xmlriver.com/search/xml?user={self.google_config.user_id}&key={self.google_config.key}&query=site:{url} {inn}'
        soup = self.check_page(new_url)
        if soup.doccount:
            return 'yes'
        
        ref_address = new_address.split(',')
        for i in range(0,len(ref_address)):
            new_ref_address = ''
            for el in ref_address[i:]:
                new_ref_address += el
            new_url = f'http://xmlriver.com/search/xml?user={self.google_config.user_id}&key={self.google_config.key}&query=site:{url} {new_ref_address}'
            soup = self.check_page(new_url)
            if soup.doccount:
                return 'yes'

        return 'no'

    def parce(self, organization: dict) -> list[dict]|None:

        organization_list = []
        reg_url = r'^(?:https?:\/\/)?(?:www\.)?([^\/:?#]+)(?:\/([^\/:?#]+))?'
        url = f'http://xmlriver.com/search/xml?user={self.google_config.user_id}&key={self.google_config.key}&query={organization["name_full"]}'
        check = self.check_page(url)

        data_urls = []
        if check.text.strip() == 'На вашем счету закончились деньги. Для дальнейшей работы пополните свой счет.':
            raise 'На вашем счету закончились деньги.'
        result = check.results
        if result:
            url1 = result.find(id=1).url.text
            url11 = re.search(reg_url, url1).group(1)
            data_urls.append(url11)
            try:
                url2 = result.find(id=2).url.text
                url22 = re.search(reg_url, url2).group(1)
                data_urls.append(url22)
            except AttributeError:
                data_urls.append(url11)
        else:
            return None

        if data_urls[0] == data_urls[1]:
            data_urls.pop(1)

        for url_site in data_urls:
            print(url_site)
            new_org = organization.copy()
            new_url_site = re.search(reg_url, url_site).group(1)
            if new_url_site in self.repository.sites_stop_list:
                continue

            new_org['site'] = new_url_site
            new_org['confirmation'] = self.check_google_status(new_url_site, organization['inn'], organization['address'])

            self.repository.write_db_collected_sites(organization['id'], new_url_site)
    
            sites_in_db = self.repository.check_site_in_db(new_org['id'])
            if sites_in_db:
                if new_org['site'] not in sites_in_db:
                    self.repository.write_db_site(new_org['id'], new_org['site'], new_org['confirmation'])
                    print('site added')
            else:
                self.repository.write_db_site(new_org['id'], new_org['site'], new_org['confirmation'])
                print('site added')

            new_org.pop('name_full')
            new_org.pop('inn')
            new_org.pop('address')
            organization_list.append(new_org)

        if organization_list == []:
            self.repository.write_db_status_organization(organization['id'], 'no')
            return None
        self.repository.write_db_status_organization(organization['id'], 'yes')
        return organization_list

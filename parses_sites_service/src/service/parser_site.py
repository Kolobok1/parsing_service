import re
import requests
from ..models.models import CompanyInfo
from bs4 import BeautifulSoup as bs4
from requests_html import HTMLSession

class ParserSite:
    def __init__(self, session: requests.Session, stop_email_list: list) -> None:
        self.session_h = HTMLSession()
        self.session = session
        self.stop_email_list = stop_email_list

    def __decode_email(self, e):
        de = ""
        k = int(e[:2], 16)

        for i in range(2, len(e)-1, 2):
            de += chr(int(e[i:i+2], 16)^k)

        return de

    def start(self, data: CompanyInfo) -> CompanyInfo:

        self.data = data
        self.checker_for_email = True
        url_site: str = 'http://' + self.data.site

        try:
            self.response = self.session_h.get(url=url_site, timeout=10, allow_redirects=True)
            if self.response.status_code > 299 and self.response.status_code < 400:
                url_site = url_site.replace('http://', 'https://')
                self.response = self.session_h.get(url=url_site, timeout=10, allow_redirects=False)
            try:
                self.response.html.render(timeout=65)
            except Exception as ex:
                self.checker_for_email = False

            self.soup = bs4(self.response.html.html, features="lxml")

        except Exception as err:
            print(err)
            self.data.status = 'no'
            self.data.confirmation = 'no'
            return self.data

        if self.response:
            self.data.status = 'yes'
        else:
            self.data.status = 'no'
            return self.data

        self.get_title()
        self.check_analytics()
        self.get_email()

        if self.data.title != 'no' and self.data.confirmation == 'yes':
            self.data.confirmation = 'yes'
        elif self.data.confirmation == None:
            self.data.confirmation = None
        else:
            self.data.confirmation = 'no'
        
        return self.data

    def get_title(self) -> None:

        if self.soup.find('title'):
            try:
                self.data.title = self.soup.find('title').string[:600]
            except Exception as ex:
                self.data.title = 'no'
        if self.soup.find('meta', attrs={'name': 'description'}):
            try:
                self.data.description = self.soup.find('meta', attrs={'name': 'description'})['content'][:1000]
            except Exception as ex:
                self.data.description = 'no'
        if self.data.description == '':
            self.data.description = 'no'

        if self.data.title == 'Истёк срок регистрации домена':
            self.data.status = 'no'
            self.data.confirmation = 'no'

    def check_analytics(self) -> None:

        scripts = self.soup.find_all('script')

        for script in scripts:
            if script.get('src'):
                if 'mc.yandex.ru/metrika' in script.get('src'):
                    self.data.yandex = 'yes'
            if script.string and 'mc.yandex.ru/metrika' in script.string:
                self.data.yandex = 'yes'

            if script.get('src'):
                if 'google-analytics.com/analytics.js' in script.get('src') or 'gtag/js' in script.get('src'):
                    self.data.google = 'yes'
            if script.string:
                if 'google-analytics.com/analytics.js' in script.string or 'gtag/js' in script.string:
                    self.data.google = 'yes'
                if 'ga(' in script.string or 'gtag(' in script.string:
                    self.data.google = 'yes'
            if self.data.yandex == 'yes' and self.data.google == 'yes':
                break

    def get_email(self) -> None:
        email_list = []
        reg_list = []
        email = ''
        regex = r'\b[^/:][A-Za-z0-9\.\_\%\+\-]+@[A-Za-z0-9\.\-\_]+\.[A-Z|a-z]{2,7}\b'

        if self.checker_for_email == False:
            emails_decoded = re.findall(r'data-cfemail="\w+', str(self.soup))
            if emails_decoded != []:
                for el in emails_decoded:
                    email_el = el.replace('data-cfemail="', '').strip()
                    email_list.append(self.__decode_email(email_el))
            else:
                self.checker_for_email = True

        if self.checker_for_email == True:
            tl = self.soup.find_all(string=lambda string: '@' in string)

            if tl:
                for t in tl:
                    sobaka = t.find('@')
                    if len(t)>150:
                        start = sobaka - 35
                        end = sobaka + 35
                        res = t[start:end]
                    else:
                        res = t

                    res_regex = re.findall(regex, res)

                    if res_regex != []:
                        for el in res_regex:
                            if 'sentry' in el:
                                continue
                            reg_list.append(el)

                    for el in reg_list:
                        el = el.strip().lower()
                        email_list.append(el)
            else:
                self.data.email = None
                return

        if email_list != []:
            email_list = list(set(email_list))

        if len(email_list) == 1:
            if el in self.stop_email_list:
                self.data.email = None
                return
            email = email_list[0]
        else:
            for el in email_list:
                if el in self.stop_email_list:
                    continue
                if el != None:
                    email += el + ', '
        if email == '':
            email = None
        elif len(email) > 1000:
            email = email[:1000]
        self.data.email = email

import pymysql
import datetime
from typing import Optional
from ..config.config import MysqlConf

class Repository():
    def __init__(self, mysql_config: MysqlConf) -> None:
        self.config = mysql_config
        self.connection = self.__connection_open()
        self.sites_stop_list = []
        for i in self.get_stop_site():
            self.sites_stop_list.append(i['site'])

    def __connection_open(self):
        connection = pymysql.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database,
            cursorclass=pymysql.cursors.DictCursor
        )
        print('[[ok]]')
        return connection

    def get_stop_site(self) -> list[str]:

        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT site FROM site_stop_list;"
            )
            sites_stop_list = cursor.fetchall()
            return sites_stop_list

    def check_site_in_db(self, organization_id: int) -> Optional[list]:

        site_list = []
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT site FROM sites WHERE organization_id = %s;",
                (organization_id)
            )
            sites = cursor.fetchall()
            if sites:
                for site in sites:
                    site_list.append(site['site'])
                return site_list
            return None

    def write_db_collected_sites(self, organization_id: int, site: str) -> None:

        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT sites_test (organization_id, site, created_at) VALUES (%s, %s, %s);",
                (
                    organization_id,
                    site,
                    datetime.datetime.now()
                )
            )
            self.connection.commit()

    def write_db_status_organization(self, organization_id: int, site_status: str) -> None:

        with self.connection.cursor() as cursor:
            cursor.execute(
                """UPDATE organizations SET 
                site_status = %s,
                site_check_date = %s 
                WHERE id = %s;
                """,
                (   
                    site_status,
                    datetime.datetime.now(),
                    organization_id
                )
            )
            self.connection.commit()

    def write_db_site(self, id_organization: int, site: str, confirmation: str) -> None:

        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT sites (
                organization_id,
                site,
                confirmation,
                created_at
                ) VALUES (%s, %s, %s, %s);""",
                (
                    id_organization,
                    site,
                    confirmation,
                    datetime.datetime.now()
                )
            )
            self.connection.commit()

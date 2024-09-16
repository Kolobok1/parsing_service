import pymysql
import datetime
from ..config.config import MysqlConf

class Repository():
    def __init__(self, mysql_config: MysqlConf) -> None:
        self.config = mysql_config
        self.connection = self.__connection_open()

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

    def get_stop_email(self) -> list:

        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT email FROM email_stop_list;"
            )
            email_stop_list = cursor.fetchall()
            return email_stop_list

    def update_db_site(self, data: dict) -> None:

        with self.connection.cursor() as cursor:
            cursor.execute(
                """UPDATE sites SET
                status = %s,
                confirmation = %s,
                title = %s,
                description = %s,
                yandex_metrika = %s,
                google_analytics = %s,
                emails = %s,
                updated_at = %s
                WHERE organization_id = %s and
                site = %s;""",
                (
                    data['status'],
                    data['confirmation'],
                    data['title'],
                    data['description'],
                    data['yandex'],
                    data['google'],
                    data['email'],
                    datetime.datetime.now(),
                    data['organization_id'],
                    data['site']
                )
            )
            self.connection.commit()

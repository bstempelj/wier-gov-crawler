import psycopg2
from dbconfig import config
from os.path import splitext
import requests


class Database:
    data_types = None
    use_db = True

    def __init__(self, use_db):
        self.conn = None
        self.use_db = use_db

        if use_db:
            self.connect()

    def connect(self):
        """ Connect to the PostgreSQL database server """
        try:
            # read connection parameters
            params = config('../config/database.ini')

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self.conn = psycopg2.connect(**params)
            print('Connection to DB successful')

            self.conn.cursor().execute("ALTER SEQUENCE crawldb.page_id_seq RESTART WITH 1;" \
                                        "ALTER SEQUENCE crawldb.page_data_id_seq RESTART WITH 1;" \
                                        "ALTER SEQUENCE crawldb.site_id_seq RESTART WITH 1;")
            print('Delete data from image table')
            self.conn.cursor().execute("DELETE FROM crawldb.image")
            print('Delete data from page_data table')
            self.conn.cursor().execute("DELETE FROM crawldb.page_data")
            print('Delete data from page table')
            self.conn.cursor().execute("DELETE FROM crawldb.page")
            print('Delete data from site table')
            self.conn.cursor().execute("DELETE FROM crawldb.site")
            print('INSERT IMAGE code to page_type table')
            self.conn.cursor().execute("INSERT INTO crawldb.page_type (code) VALUES ('IMAGE') ON CONFLICT (code) DO UPDATE SET code = 'IMAGE'")
            self.conn.commit()

            # Get all page types from database
            cur = self.conn.cursor()
            cur.execute("SELECT code FROM crawldb.data_type")
            self.data_types = cur.fetchall()

            for idx, row in enumerate(self.data_types):
                self.data_types[idx] = row[0]

            return self.conn
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def add_site(self, site, robot, sitemap):
        if not self.use_db:
            return

        cur = self.conn.cursor()
        cur.execute("INSERT INTO crawldb.site(domain, robots_content, sitemap_content) "
                    "VALUES (%s, %s, %s) RETURNING id", (site, robot, sitemap,))
        site_id = cur.fetchone()[0]
        self.conn.commit()

        return site_id

    def add_page(self, url, html_content, http_code, accessed_time, site_id):
        if not self.use_db:
            return

        cur = self.conn.cursor()

        doc = self._check_if_doc(url)

        # if document then html_content must be None and write content in page_data table
        row = (site_id, doc[0], url, html_content if doc[1] is None else None, http_code, accessed_time,)

        try:
            cur.execute("INSERT INTO crawldb.page(site_id, page_type_code, url, html_content, http_status_code, accessed_time) "
                        "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (url) DO UPDATE SET url = '" + url + "'  RETURNING id", row)
            page_id = cur.fetchone()[0]

            # if file write to page_data table
            if doc[0] == 'BINARY':
                cur.execute(
                    "INSERT INTO crawldb.page_data(page_id, data_type_code, data) "
                    "VALUES (%s, %s, %s)", (page_id, doc[2], doc[1],))
                self.conn.commit()
            elif doc[0] == 'IMAGE':
                cur.execute(
                    "INSERT INTO crawldb.image(page_id, filename, content_type, data, accessed_time) "
                    "VALUES (%s, %s, %s, %s, %s)", (page_id, doc[3], doc[2], doc[1], accessed_time,))
                self.conn.commit()

        except Exception as e:
            print(e)
            print(row)
            return

        self.conn.commit()

    def get_connection(self):
        return self.conn

    def close_connection(self):
        self.conn.cursor().close()

    def _check_if_doc(self, url):
        path, ext = splitext(url)
        data_type_code = ext[1:].upper()
        if data_type_code in self.data_types:
            data = requests.get(url)
            return 'BINARY', data.content, data_type_code
        elif ext in [".png", ".jpg", ".jpeg", ".gif"]:
            data = requests.get(url)
            filename = path[path.rindex("/")+1:]
            return 'IMAGE', data.content, ext[1:].upper(), filename
        else:
            return 'HTML', None

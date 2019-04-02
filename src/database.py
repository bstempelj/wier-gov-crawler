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

    def _check_if_page_exists(self, hash_content):
        cur = self.conn.cursor()

        cur.execute("SELECT id FROM crawldb.page WHERE hash_content = '" + hash_content + "'")
        return True if cur.fetchone() is not None else False

    def add_page(self, url, html_content, http_code, accessed_time, site_id, from_page, hash_content):
        if not self.use_db:
            return

        # print(hash_content)
        cur = self.conn.cursor()

        is_duplicate = self._check_if_page_exists(hash_content)
        doc = self._check_if_doc(url, is_duplicate)
        if doc == -1:
            return doc

        if doc[1] is not None or is_duplicate:
            html_content = None
            hash_content = None

        # if document then html_content must be None and write content in page_data table
        row = (site_id, doc[0], url, html_content, http_code, accessed_time, hash_content,)

        try:
            cur.execute("INSERT INTO crawldb.page(site_id, page_type_code, url, html_content, http_status_code, accessed_time, hash_content) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (url) DO UPDATE SET url = '" + url + "'  RETURNING id", row)
            page_id = cur.fetchone()[0]

            self.add_link(from_page, page_id)

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
            return -1

        self.conn.commit()
        return page_id

    def add_link(self, from_page, to_page):
        if not self.use_db:
            return

        try:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO crawldb.link(from_page, to_page) "
                "VALUES (%s, %s) ON CONFLICT (from_page, to_page) DO NOTHING", (from_page, to_page,))
            self.conn.commit()
        except Exception as e:
            print(e)

    def get_connection(self):
        return self.conn

    def close_connection(self):
        self.conn.cursor().close()

    def _check_if_doc(self, url, is_duplicate):
        path, ext = splitext(url)
        data_type_code = ext[1:].upper()
        if data_type_code in self.data_types:

            try:
                data = requests.get(url)
            except Exception as e:
                print(e)
                return -1

            return 'BINARY', data.content, data_type_code
        elif ext in [".png", ".jpg", ".jpeg", ".gif"]:

            try:
                data = requests.get(url)
            except Exception as e:
                print(e)
                return -1

            filename = path[path.rindex("/")+1:]
            return 'IMAGE', data.content, ext[1:].upper(), filename
        else:
            return 'DUPLICATE' if is_duplicate else 'HTML' , None

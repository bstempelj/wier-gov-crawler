import psycopg2
from dbconfig import config


class Database:
    site_id = -1

    def __init__(self):
        self.conn = None
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

            print('Delete data from page table')
            self.conn.cursor().execute("DELETE FROM crawldb.page")
            print('Delete data from site table')
            self.conn.cursor().execute("DELETE FROM crawldb.site")
            self.conn.commit()

            return self.conn
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def add_site(self, site, robot, sitemap):
        cur = self.conn.cursor()

        cur.execute("SELECT id FROM crawldb.site WHERE domain = '" + site + "'")
        id = cur.fetchone()

        # Insert site if not yet inserted
        if id is None:
            cur.execute("INSERT INTO crawldb.site(domain, robots_content, sitemap_content) "
                        "VALUES (%s, %s, %s) RETURNING id", (site, robot, sitemap, ))
            self.site_id = cur.fetchone()[0]
            self.conn.commit()

        """
        cur.execute("INSERT INTO crawldb.site(domain, robots_content, sitemap_content) "
                    "SELECT '" + site + "' as domain, '" + robot + "' as robots_content, '" + sitemap + "' as sitemap_content "
                    "FROM crawldb.site "
                    "WHERE domain != '" + site + "' RETURNING id")
        """

    def add_page(self, url, html_content, http_code, accessed_time):
        cur = self.conn.cursor()

        row = (self.site_id, 'HTML', url, html_content, http_code, accessed_time,)

        try:
            cur.execute("INSERT INTO crawldb.page(site_id, page_type_code, url, html_content, http_status_code, accessed_time) "
                        "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (url) DO UPDATE SET url = '" + url + "'", row)
        except Exception:
            return

        self.conn.commit()

    def get_connection(self):
        return self.conn

    def close_connection(self):
        self.conn.cursor().close()

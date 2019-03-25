import psycopg2
from dbconfig import config

conn = None


def connect():
    """ Connect to the PostgreSQL database server """
    global conn
    try:
        # read connection parameters
        params = config('../config/database.ini')

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        #cur = conn.cursor()

        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def write_url():
    global conn
    cur = conn.cursor()




def get_connection():
    return conn


def close_connection():
    conn.cursor().close()


if __name__ == '__main__':
    connect()

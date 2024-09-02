"""

    State.py



    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center

"""
import datetime
import sqlite3


class State:

    def __init__(self, domain, resolution, name, dbconf):
        if not isinstance(domain, str):
            raise ValueError('Domain must be a string')
        if not isinstance(resolution, str):
            raise ValueError('Resolution must be a string')
        if not isinstance(name, str):
            raise ValueError('Name must be a string')
        if 'driver' not in dbconf:
            raise ValueError('Configuration database name not defined')
        if 'user' not in dbconf:
            raise ValueError('Configuration database user not defined')
        if 'password' not in dbconf:
            raise ValueError('Configuration database password not defined')
        if 'url' not in dbconf:
            raise ValueError('Configuration database vendor not defined')
        if 'logintimeout' not in dbconf:
            raise ValueError('Configuration database login timeout not defined')

        self.domain = domain
        self.resolution = resolution
        self.name = name
        self.dbconf = dbconf
        self.dbconf['readonly'] = 'on'
        self.dbconn = None
        self.domain_id = None
        self.resolution_id = None
        self.time = None
        self.csv = ''

        self.openDb()

        sqlquery = f"SELECT id FROM domain WHERE name = '{self.domain}'"
        try:
            self.dbconn.execute(sqlquery)
            results = self.dbconn.fetchall()
        except Exception as e:
            raise ValueError(f"Error querying for domain: {str(e)}")

        if len(results) == 1:
            self.domain_id = results[0][0]
        elif len(results) == 0:
            raise ValueError("No rows obtained querying for domain")
        else:
            raise ValueError("Multiple rows obtained querying for domain")

        sqlquery = f"SELECT id FROM resolution WHERE name = '{self.resolution}'"
        try:
            self.dbconn.execute(sqlquery)
            results = self.dbconn.fetchall()
        except Exception as e:
            raise ValueError(f"Error querying for resolution: {str(e)}")

        if len(results) == 1:
            self.resolution_id = results[0][0]
        elif len(results) == 0:
            raise ValueError("No rows obtained querying for resolution")
        else:
            raise ValueError("Multiple rows obtained querying for resolution")

        self.closeDb()

    def get(self):
        self.openDb()

        sqlquery = f"SELECT time, csv FROM state WHERE name = '{self.name}' AND domain_id = {self.domain_id} AND resolution_id = {self.resolution_id}"
        try:
            self.dbconn.execute(sqlquery)
            results = self.dbconn.fetchall()
        except Exception as e:
            raise ValueError(f"Database query error: {str(e)}")

        if len(results) > 0:
            self.time = datetime.datetime.strptime(results[0][0], '%Y-%m-%d %H:%M:%S.%f')
            if results[0][1] is not None:
                self.csv = results[0][1]
        else:
            self.time = None
            self.csv = ''

        self.closeDb()

    def write(self):
        useUpdate = self.entryExists()
        self.time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        self.dbconf['readonly'] = 'off'
        self.openDb()

        if useUpdate:
            self.dbconn.execute(f"UPDATE state SET time = '{self.time}', csv = '{self.csv}' WHERE name = '{self.name}' AND domain_id = {self.domain_id} AND resolution_id = {self.resolution_id}")
        else:
            self.dbconn.execute(f"INSERT INTO state (domain_id, resolution_id, name, time, csv) VALUES ({self.domain_id}, {self.resolution_id}, '{self.name}', '{self.time}', '{self.csv}')")

        self.closeDb()
        self.dbconf['readonly'] = 'on'

        self.get()

    def remove(self):
        if self.entryExists():
            self.dbconf['readonly'] = 'off'
            self.openDb()

            sqlquery = f"DELETE FROM state WHERE name = '{self.name}' AND domain_id = {self.domain_id} AND resolution_id = {self.resolution_id}"
            self.dbconn.execute(sqlquery)

            self.closeDb()
            self.dbconf['readonly'] = 'on'

            self.get()

    def openDb(self):
        try:
            self.dbconn = sqlite3.connect(self.dbconf['url'])
        except Exception as e:
            raise ValueError(f"Failed to connect to configuration database: {str(e)}")

    def closeDb(self):
        if self.dbconn is not None:
            self.dbconn.close()

    def entryExists(self):
        self.openDb()

        sqlquery = f"SELECT COUNT(*) FROM state WHERE name = '{self.name}' AND domain_id = {self.domain_id} AND resolution_id = {self.resolution_id}"
        try:
            self.dbconn.execute(sqlquery)
            results = self.dbconn.fetchall()
        except Exception as e:
            raise ValueError("Query error during entryExists call")

        e = bool(results[0][0])

        self.closeDb()

        return e

import json
import os
import sqlite3
from flask import Flask, request
from flask_restful import Resource, Api

# Maximum number of rows to retain - older rows will be deleted to minimise disk usage
MAX_ROWS = 336

# SQLite3 .db filename
DB_FILE = os.environ['HOME']+ "/.xDripAPS_data/xDripAPS.db"

app = Flask(__name__)
api = Api(app)

def create_schema():
    conn = sqlite3.connect(DB_FILE)
    qry = """CREATE TABLE entries
            (device text,
            date numeric,
            dateString text,
            sgv numeric,
            direction text,
            type text,
            filtered numeric,
            unfiltered numeric,
            rssi numeric,
            noise numeric)"""

    conn.execute(qry)
    conn.commit() # Required?
    conn.close()

def startup_checks():
    # Does .db file exist?
    if os.path.isfile(DB_FILE):
        # Check for corruption
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("PRAGMA integrity_check")
        status = str(c.fetchone()[0])
        if status == "ok":
            print "Startup checks OK"
            conn.close()
        else:
            print "Startup checks FAIL"
            # Delete corrupt database
            print "Deleting corrupt SQLite database file (" + DB_FILE + ")..."
            conn.close()
            os.remove(DB_FILE)
            # re-create database
            print "Re-cresting database..."
            create_schema()
    else:
        # Database doesn't exist, so create it
        create_schema()

class Entries(Resource):

    def get(self):

    	# Connect to database
    	conn = sqlite3.connect(DB_FILE)

    	# Housekeeping first
    	qry =  "DELETE FROM entries WHERE ROWID IN "
    	qry += "(SELECT ROWID FROM entries ORDER BY ROWID DESC LIMIT -1 OFFSET " + str(MAX_ROWS) + ")"
    	conn.execute(qry)
    	conn.commit()

    	# Get count parameter
    	count = request.args.get('count')

    	# Perform query and return JSON data
        qry  = "SELECT ROWID as _id, device, date, dateString, sgv, direction, type, filtered, "
        qry += "unfiltered, rssi, noise "
        qry += "FROM entries ORDER BY date DESC"
        if count != None:
            qry += " LIMIT " + count

        results_as_dict = []

        cursor = conn.execute(qry)

        for row in cursor:
            result_as_dict = {
#		'_id' : row[0],
                'device' : row[1],
                'date' : row[2],
                'dateString' : row[3],
                'sgv' : row[4],
                'direction' : row[5],
                'type' : row[6],
                'filtered' : row[7],
                'unfiltered' : row[8],
                'rssi' : row[9],
                'noise' : row[10],
	            'glucose' : row[4]}
            results_as_dict.append(result_as_dict)

        conn.close()
	return results_as_dict

    def post(self):

        # Get hashed API secret from request
        request_secret_hashed = request.headers['Api_Secret']
        print 'request_secret_hashed : ' + request_secret_hashed

        # Get API_SECRET environment variable
        env_secret_hashed = os.environ['API_SECRET']

        # Authentication check
        if request_secret_hashed != env_secret_hashed:
            print 'Authentication failure!'
            print 'API Secret passed in request does not match API_SECRET environment variable'
            return 'Authentication failed!', 401

        # Get JSON data
        json_data = request.get_json(force=True)

        conn = sqlite3.connect(DB_FILE)

        # build qry string
        qry  = "INSERT INTO entries (device, date, dateString, sgv, direction, type, "
        qry += "filtered, unfiltered, rssi, noise) "
        qry += "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

        # list of successfully inserted entries, to return
        inserted_entries = []

        # Get column values (json_data will contain exactly one record if data source is xDrip
        # but could contain more than one record if data source is xDripG5 for iOS)
        for entry in json_data:
            device          = entry['device']
            date            = entry['date']
            dateString      = entry['dateString']
            sgv             = entry['sgv']
            direction       = entry['direction']
            type            = entry['type']
            filtered        = entry['filtered'] if 'filtered' in entry else None
            unfiltered      = entry['unfiltered'] if 'unfiltered' in entry else None
            rssi            = entry['rssi'] if 'rssi' in entry else None
            noise           = entry['noise'] if 'noise' in entry else None

            # Perform insert
            try:
                conn.execute(qry, (device, date, dateString, sgv, direction, type, filtered, unfiltered, rssi, noise))
                conn.commit()
            except sqlite3.Error:
                continue

            inserted_entries.append(entry)

        conn.close()

        # return entries that have been added successfully
        return inserted_entries, 200

class Test(Resource):
    def get(self):
        # Get hashed API secret from request
        request_secret_hashed = request.headers['Api_Secret']
        print 'request_secret_hashed : ' + request_secret_hashed

        # Get API_SECRET environment variable
        env_secret_hashed = os.environ['API_SECRET']

        # Authentication check
        if request_secret_hashed != env_secret_hashed:
            print 'Authentication failure!'
            print 'API Secret passed in request does not match API_SECRET environment variable'
            return 'Authentication failed!', 401

        return {"status": 'ok'}

api.add_resource(Entries, '/api/v1/entries')
api.add_resource(Test, '/api/v1/experiments/test')

if __name__ == '__main__':
    startup_checks()
    app.run(host='0.0.0.0')

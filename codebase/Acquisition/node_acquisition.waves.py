"""

   node_acquisition_waves.py
    script to acquire radial files from the portals.


    changes
      2018-06-12 - Initial version
      2019-02-11 - Check to see if the node_rsync_dir has a trailing '/'.  Add it if not
      2019-03-05 - Remove cursor close statements, added db_data.close in scriptExit
      2019-04-11 - Added port to database connections
      2019-04-25 - Changed error messages on mysql connect.  Fixed Bugs
      2019-06-11 - Added "Script finished" to scriptExit()
      2019-07-08 - Added disabled column in portal
      2019-08-30 - Bug: Changed port for data_database from database to data_database
      2019-08-30 - If log dir doesn't exist, create it
      2019-09-06 - Bug: change myfile to filenotcopied in scriptExit
      2019-09-25 - Added option to connect with ssl for data_database
      2019-09-26 - Added option to connect with ssl for database
      2020-01-16 - Added --ignore-missing-args to rsync.  In case files are removed before rsync finishes
      2020-05-20 - Added filesnotcopied empty variable
      2020-05-27 - Removed -t option in rsync, check for any errors during filecopy
      2020-10-23 - If insertIntoDB returns false, run scriptExit
      2020-10-13 - Added option to rsync from localhost for sshkey_node
      2020-11-16 - Bug: fixed sql for specifying a portal
      2022-01-25 - Bug: Fixed log rotate
      2022-03-02 - Removed log rotate
      2023-01-17 - Forked to retrieve wave files


   HF-Radar Network
   Scripps Institution of Oceanography
   Coastal Observing Research and Development Center

"""
import argparse
import configparser
import logging
import os
# import re
import shutil
# import socket
import subprocess
import sys
# import time
import pymysql
# from lib.cordc_lib import grep
from lib.wavefile import WaveFile


def scriptExit():
    """
    Cleanly exit my script. Close my databases, and make sure any files that
    didn't get copied to the database get removed from the holding dir.
    """
    logging.debug("scriptExit called")

    db.close()
    db_data.close()

    # These files haven't gotten processed, therefore, remove them from the holding dir
    # so the next rsync will find them
    for filenotcopied in filesnotcopied:
        filenotcopied = "{}{}".format(node_holding_dir, filenotcopied.strip("'"))
        logging.debug("filenotcopied: {}".format(filenotcopied))
        if os.path.exists(filenotcopied) and os.path.isfile(filenotcopied):
            logging.info("Removing {} to be rsync'd again.".format(filenotcopied))
            os.remove(filenotcopied)

    logging.info("Script finished")
    sys.exit()


# End scriptExit

LOG_DIR = "log"
LOG_FILENAME = "%s/%s.log" % (LOG_DIR, os.path.splitext(os.path.basename(__file__))[0])
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Define this script's location
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Define my command line arguments
parser = argparse.ArgumentParser(description="Acquire new waves from portals using rsync.")
parser.add_argument("-p", help="The portal to retrieve from (e.g. SIO, SLO).  Defaults to all portals")
parser.add_argument("-t0", help="Epoch start date in relation to the file modification time.  This will supersede the state time in the database")
parser.add_argument("-t1", help="Epoch end date in relation to the file modification time.  Use of this will prevent the last state time from updating in the database")
parser.add_argument("-ini", help="Location of a ini config file to use", default="acquisition.ini")
parser.add_argument("-v", action="store_true", help="Display debugging messages")
args = parser.parse_args()

# Read my ini file
config = configparser.ConfigParser()
config.read_file(open(args.ini))

# Setup my logger, use one log file or one log file per station?
if args.v:
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO
logging.basicConfig(filename=LOG_FILENAME, level=loglevel, format="%(asctime)s %(levelname)s: %(message)s")

# Setup the database connection
try:
    if config.has_option("database", "ssl_ca"):
        db = pymysql.connect(
            user=config["database"]["user"],
            passwd=config["database"]["passwd"],
            host=config["database"]["host"],
            db=config["database"]["db"],
            port=int(config["database"]["port"]),
            ssl={"ssl": {"ca": config["database"]["ssl_ca"], "key": config["database"]["ssl_client_key"], "cert": config["database"]["ssl_client_cert"]}},
            cursorclass=pymysql.cursors.DictCursor,
        )
    else:
        db = pymysql.connect(
            user=config["database"]["user"],
            passwd=config["database"]["passwd"],
            host=config["database"]["host"],
            db=config["database"]["db"],
            port=int(config["database"]["port"]),
            cursorclass=pymysql.cursors.DictCursor,
        )
except pymysql.Error as e:
    code = e.code
    msg = e.args[code]
    logging.error("Unable to connect to MySQL database - %s: %s", config["database"]["db"], msg)
    sys.exit()

try:
    if config.has_option("data_database", "ssl_ca"):
        db_data = pymysql.connect(
            user=config["data_database"]["user"],
            passwd=config["data_database"]["passwd"],
            host=config["data_database"]["host"],
            db=config["data_database"]["db"],
            port=int(config["data_database"]["port"]),
            ssl={"ssl": {"ca": config["data_database"]["ssl_ca"], "key": config["data_database"]["ssl_client_key"], "cert": config["data_database"]["ssl_client_cert"]}},
            cursorclass=pymysql.cursors.DictCursor,
        )
    else:
        db_data = pymysql.connect(
            user=config["data_database"]["user"],
            passwd=config["data_database"]["passwd"],
            host=config["data_database"]["host"],
            db=config["data_database"]["db"],
            port=int(config["data_database"]["port"]),
            cursorclass=pymysql.cursors.DictCursor,
        )
except pymysql.Error as e:
    code = e.code
    msg = e.args[code]
    logging.error("Unable to connect to MySQL database - %s: %s", config["database"]["db"], msg)
    sys.exit()

with db.cursor() as cur:
    sql = "SELECT * FROM portal p WHERE disabled=0"
    sql_where = []
    if args.p:
        sql_where.append("p.name='" + args.p + "'")
        sql = sql + " AND " + " AND ".join(sql_where)
    logging.debug("SQL: %s", sql)

    try:
        cur.execute(sql)
    except pymysql.Error as e:
        cur.close()
        db.close()
        code, msg = e.args
        logging.error("Unable to retrieve list of portals from the database: %s", msg)
        sys.exit()

    for row in cur:

        logging.info("Checking rsync for new files from portal %s", row["name"])

        filesnotcopied = []

        # Check to see if the node_rsync_dir has a trailing '/'
        if not row["wave_node_rsync_dir"].endswith("/"):
            row["wave_node_rsync_dir"] = row["wave_node_rsync_dir"] + "/"

        # create my node holding dir
        node_holding_dir = config["directories"]["waves_node_holding"]
        if config["directories"]["waves_node_holding"][-1:] != "/":
            node_holding_dir = "%s/" % node_holding_dir
        # if node_holding_dir doesn't exist, create it
        if not os.path.isdir(node_holding_dir):
            logging.debug("Creating %s", node_holding_dir)
            os.makedirs(node_holding_dir, exist_ok=True)

        # Run my rsync command
        if row["sshkey_node"] == "localhost":
            rsync = ["rsync", "-crm", "--log-file=log/" + row["name"] + ".log", "--log-file-format='%n'", "--out-format='%n'", "--ignore-missing-args", row["wave_node_rsync_dir"], node_holding_dir]

        else:
            rsync = [
                "rsync",
                "-crm",
                "--log-file=log/" + row["name"] + ".log",
                "--log-file-format='%n'",
                "--out-format='%n'",
                "--ignore-missing-args",
                row["sshkey_node"] + ":" + row["wave_node_rsync_dir"],
                node_holding_dir,
            ]
        try:
            completed = subprocess.check_output(rsync, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            logging.error("rsync failed: %s", exc.output.decode("ascii"))
        else:
            # if all goes well, read the output from completed.decode('ascii')
            # and make sure each file passes QC and then copy the file to another
            # directory

            # Need to put the list of files rsynced into a list.  If we are not able to finish the script, remove the files from the holding dir
            myrsyncfiles = completed.decode("ascii").split("\n")
            # Remove the last item in the rsync command list
            # The last contains empty spaces
            filesnotcopied = myrsyncfiles[:-1]
            for mydirfile in myrsyncfiles:
#               if not "wls" in mydirfile:
                if "wls" not in mydirfile:
                    continue

                logging.info("rsync found file: %s", mydirfile)
                mydirfile = mydirfile.replace("'", "")

                rf = WaveFile(node_holding_dir + mydirfile)

                # Set ini file
                if not rf.setIniFile(args.ini):
                    # if we can't set the inifile, we want to exi
                    scriptExit()

                # if we set t0 or t1 check them with the file modification time
                if args.t0:
                    if rf.modificationTime < args.t0:
                        continue
                if args.t1:
                    if rf.modificationTime > args.t1:
                        continue

                # validate the inner metadata of the file
                if not rf.validFile():
                    logging.error("%s%s not valid", node_holding_dir, mydirfile)
                    filesnotcopied.remove("'{}'".format(mydirfile))
                    continue

                # Once the file has been validated, save the file into the database and its final resting place.
                df = mydirfile.split("/")
                net = df[0]
                sta = df[1]
                with db_data.cursor() as cur_data:
                    # Check to see if the network is in the db
                    sql = "SELECT network_id from network where net='{}'".format(net)
                    logging.debug("SQL: %s", sql)
                    try:
                        numrows = cur_data.execute(sql)
                    except pymysql.Error as e:
                        code, msg = e.args
                        logging.error("Unable to retrieve network id for {}: {}.  Skipping file.".format(net, msg))
                        continue
                    # If the network isn't in the db
                    if numrows == 0:
                        # Add the network
                        sql = "insert ignore into network (net) values('{}')".format(net)
                        try:
                            cur_data.execute(sql)
                            db_data.commit()
                        except pymysql.Error as e:
                            code, msg = e.args
                            logging.error("Unable to insert network {} into database: {}.  Skipping file.".format(net, msg))
                            continue
                        network_id = cur_data.lastrowid
                    else:
                        rs = cur_data.fetchone()
                        network_id = rs["network_id"]
                    logging.debug("network id for {} is {}".format(net, network_id))

                    # Check to see if the site is in the db
                    sql = "SELECT s.site_id from site s left join network n ON s.network_id = n.network_id where sta='{}' and net='{}'".format(sta, net)
                    logging.debug("SQL: %s", sql)
                    try:
                        numrows = cur_data.execute(sql)
                    except pymysql.Error as e:
                        code, msg = e.args
                        logging.error("Unable to retrieve station id for {}: {}.  Skipping file.".format(sta, msg))
                        continue
                    # If the station isn't in the db
                    if numrows == 0:
                        # Add the station
                        sql = "insert ignore into site (network_id,sta) values({},'{}')".format(network_id, sta)
                        try:
                            cur_data.execute(sql)
                            db_data.commit()
                        except pymysql.Error as e:
                            code, msg = e.args
                            logging.error("Unable to insert sta {} into database: {} {}.  Skipping file.".format(sta, sql, msg))
                            continue
                        site_id = cur_data.lastrowid
                    else:
                        rs = cur_data.fetchone()
                        site_id = rs["site_id"]
                    logging.debug("site id for {} is {}".format(sta, site_id))

                # Insert into database. Make sure insert into database returns correctly before copying files
                logging.info("Attempting to insert data into the database")
                if rf.insertIntoDB():
                    mydir, myfile = os.path.split(mydirfile)
                    finaldir = "%s%s" % (config["directories"]["waves_node_final_dir"], mydir)

                    if not os.path.isdir(finaldir):
                        logging.debug("Creating %s", finaldir)
                        os.makedirs(finaldir, exist_ok=True)
                    try:
                        logging.info("Moving %s to %s", myfile, finaldir)
                        shutil.copy2(node_holding_dir + mydirfile, finaldir + "/" + myfile)

                        # Adding double quotes because the entries in filesnotcopied have it, but for some reason mydirfile doesn't
                        filesnotcopied.remove("'{}'".format(mydirfile))
                    except:
                        # If there's an error copy the file to the final dir, remove it from the holding dir so we can rsync it again
                        logging.error("Unable to copy %s%s to %s" % (node_holding_dir, mydirfile, finaldir))
                        os.remove(node_holding_dir + mydirfile)

                # Insert didn't work, remove the file from the node_holding_dir so it can be synced later againh
                else:
                    logging.error("insertIntoDB failed.  Removing %s%s to be rsynced later" % (node_holding_dir, mydirfile))
                    scriptExit()

                logging.debug("File finished")
        logging.info("Finished rsyncing with portal %s", row["name"])
scriptExit()

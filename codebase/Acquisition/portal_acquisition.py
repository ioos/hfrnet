"""

    portal_acquisition

    Script to acquire radial files from various sites.  Files are
    rsynced into the portal and QC'd before eventually getting copied
    into another directory that the nodes use to rsync with.

    changes
      2018-06-12 - Initial version
      2018-06-15 - Changed holding dir to have similar structure to final dir in node
      2018-09-13 - If t1 is defined, don't set statetime
      2018-10-15 - Changed default config file from portal_acquisition.ini to acquisition.ini
      2018-11-06 - Small changes
      2018-11-27 - Removed def emailErrors
      2019-02-26 - Try and update the state time in the master.  On errors, update the local
      2019-04-08 - Create log directory, if it doesn't exist
      2019-04-11 - Added port to mysql connections
      2019-04-11 - Make sure src_dir ends with '/'
      2019-04-22 - Bugfixes
      2019-05-21 - Add find command to find files after state time before running rsync
      2019-05-28 - Added -iname to find command
      2019-06-11 - Changed find to use mmin instead of newermt.  Added more error handling for rsync and find
      2019-06-14 - Bug: fixed lasttime. retrieve 2 weeks of data
      2019-07-02 - Added option for local rsync. 'localhost' in 'sshkey_host'
      2019-07-10 - Added contimeout to rsync 300 seconds.  Changed statetime to use file mod time
      2019-07-16 - Combined the rsync exceptions.  Remove files from rsync if errors
      2019-07-18 - Changed subprocess check_output to run
      2019-07-29 - Added maxdepth 1 to find.
      2019-08-26 - Moved maxdepth option before non-option.
      2019-08-26 - Changed decode from ascii to utf-8
      2020-03-25 - Added t0 check in computing lasttime
      2020-05-27 - Removed -t (preserve file modification time) from rsync
      2020-06-04 - Added back -t (some sites were getting skipped radials)
      2020-07-06 - Changes made for getting files from an rsync.net server.  Added dryrun option
      2020-08-13 - Checked find failed(3) snd rsync tderr to make sure it starts with ssh
      2020-09-02 - Remove the file if we're not able to copy to the node rsync dir
      2021-08-18 - Update statetime in the db only if the statetime from the files are after the db statetime
      2022-03-01 - Removed logrotate


   HF-Radar Network
   Scripps Institution of Oceanography
   Coastal Observing Research and Development Center

"""
import argparse
import configparser
import logging
import math
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import pymysql
# from lib.cordc_lib import grep
from lib.radialfile import RadialFile


LOG_DIR = "log"
LOG_FILENAME = "%s/%s.log" % (LOG_DIR, os.path.splitext(os.path.basename(__file__))[0])
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
#
# define this script's location
#
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
#
# define my command line arguments
#
parser = argparse.ArgumentParser(description="Acquire new radials from server using rsync.")
parser.add_argument("-n", help="The network to retrieve (e.g. SIO, SLO)")
parser.add_argument("-s", help="The station to retrieve (e.g. SDBP, HEMP)")
parser.add_argument("-t0", help="Epoch start date in relation to the file modification time.  This will supersede the state time in the database")
parser.add_argument("-t1", help="Epoch end date in relation to the file modification time.  Use of this will prevent the last state time from updating in the database")
parser.add_argument("-ini", help="Location of a ini config file to use", default="acquisition.ini")
parser.add_argument("-dryrun", action="store_true", help="Show what would have been transferred")
parser.add_argument("-v", action="store_true", help="Display debugging messages")
args = parser.parse_args()
# print( args.n )


# read my ini file
#
config = configparser.ConfigParser()
config.read_file(open(args.ini))
#
# setup my logger, use one log file or one log file per station?
#
if args.v:
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO

logging.basicConfig(filename=LOG_FILENAME, level=loglevel, format="%(asctime)s %(levelname)s: %(message)s")
#
#
# Both of the two statements return the same thing.
# This won't work always (returns 127.0.0.1 on machines having the hostname in /etc/hosts as 127.0.0.1),
# a paliative would be what gimel shows, use socket.getfqdn() instead. 
# Of course your machine needs a resolvable hostname.
#
#
# print(socket.gethostbyname(socket.gethostname()))
ip = socket.gethostbyname(socket.getfqdn())
#
# setup the database connection
#
try:
    db = pymysql.connect(
        user=config["database"]["user"],
        passwd=config["database"]["passwd"],
        host=config["database"]["host"],
        db=config["database"]["db"],
        port=int(config["database"]["port"]),
        cursorclass=pymysql.cursors.DictCursor,
    )

except pymysql.Error as e:
    code = e.msg - e.args
    logging.error("Unable to connect to MySQL database - %s: %s ", config["database"]["db"], code)
    sys.exit()

with db.cursor() as cur:

    sql = "SELECT * FROM site s left join portal p on s.portal = p.name WHERE "
    sql_where = ["s.disabled=0", "p.ip_address=%s"]
    if args.n:
        sql_where.append("s.network='" + args.n + "'")
    if args.s:
        sql_where.append("s.site='" + args.s + "'")
    sql = sql + " AND ".join(sql_where)

    logging.debug("SQL: %s", sql)

    try:
        cur.execute(sql, ip)

    except pymysql.Error as e:
        cur.close()
        db.close()
        code, msg = e.args
        logging.error("Unable to retrieve list of sites from the database: %s", msg)
        sys.exit()

    for row in cur:
        #
        logging.info("Checking rsync for new files for %s %s %s", row["network"], row["site"], row["patterntype"])
        #
        # make sure src_dir has a '/' at the end
        #
        if not row["src_dir"].endswith("/"):
            row["src_dir"] = row["src_dir"] + "/"
        #
        # create my site rsync dest dir
        #
        site_rsync_dir = config["directories"]["site_rsync"]
        if config["directories"]["site_rsync"][-1:] != "/":
            site_rsync_dir = "%s/%s/%s/%s/" % (site_rsync_dir, row["network"], row["site"], row["patterntype"])
        else:
            site_rsync_dir = "%s%s/%s/%s/" % (site_rsync_dir, row["network"], row["site"], row["patterntype"])
        #
        # if site_rsync_dir doesn't exist, create it
        #
        if not os.path.isdir(site_rsync_dir):
            logging.debug("Creating %s", site_rsync_dir)
            os.makedirs(site_rsync_dir, exist_ok=True)
        #
        #
        # - get my last state
        # - if the state hasn't been assigned yet (0), get the last 2 weeks of data
        # - get the number of minutes to retrieve from find.
        #
        if args.t0:
            lasttime = math.floor((time.time() - int(args.t0)) / 60)
        elif row["state"] == 0:
            lasttime = 20160  # math.ceil((60*60*24*14)/60)
        else:
            lasttime = math.floor((time.time() - row["state"]) / 60)

        laststate = str(lasttime)
        #
        # find files on the remote server newer than the state time and save
        # the list of files to a tmp file before running rsync
        #
        findoutput = "/tmp/portal_acquisition-%s-%s-%s" % (row["network"], row["site"], row["patterntype"])
        f = open(findoutput, "w+")
        #
        # if sshkey_host is localhost
        if row["sshkey_host"] == "localhost":
            find = ["find", row["src_dir"], "-maxdepth", "1", "-mmin", "-" + laststate, "-type", "f", "-iname", row["file_pattern"], "-exec", "basename", "{}", ";"]
        # add if option for rsync.net
        elif "rsync.net" in row["sshkey_host"]:
            what = "find " + row["src_dir"] + " -maxdepth 1 -mmin -" + laststate + " -type f -iname '" + row["file_pattern"] + "'"
            find = ["ssh", row["sshkey_host"], what]
        # regular ssh
        else:
            what = "find " + row["src_dir"] + " -maxdepth 1 -mmin -" + laststate + " -type f -iname '" + row["file_pattern"] + "' -exec basename {};"
            find = ["ssh", row["sshkey_host"], what]
        logging.debug(find)
        try:
            myfiles = subprocess.run(find, stderr=subprocess.PIPE, stdout=f)
        except subprocess.CalledProcessError as exc:
            logging.error("find failed: %s", exc.output.decode("ascii"))
            continue
        except:
            logging.error("find failed(2): %s", myfiles.stderr.decode("ascii"))
            continue
        else:
            # If the ssh command returns something.
            # ..could be an error, might be a welcome message
            if myfiles.stderr:
                # If it's an ssh error, it'll start with ssh.
                # Hopefully welcoming message won't have ssh in it.
                if myfiles.stderr.decode("utf-8").startswith("ssh"):
                    logging.error("find failed(3): %s", myfiles.stderr.decode("utf-8"))
                    continue
            # if the find command returned nothing
            if os.stat(findoutput).st_size == 0:
                logging.info("No new files found after %s", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - lasttime * 60)))
                continue
        #
        # If we're retrieving from rsync.net host, we'll need to remove the
        # directory from the filenames from the stdout of the find command
        # This is because I can't run basename in rsync.net
        #
        if "rsync.net" in row["sshkey_host"]:
            newlines = []
            with open(findoutput) as fp:
                line = fp.readline()
                while line:
                    newlines.append(os.path.basename(line))
                    line = fp.readline()
            with open(findoutput, "w") as output:
                output.write("".join(newlines))

        # Run my rsync command.
        # file_pattern is used to distinguish ideal from measured 
        # in case they are all in the same directory.
        # RDLi_SDPL_2018_05_21_2100.ruv - codar
        # RDL_jek_2016_10_23_125300.ruv - wera
        # VIR_2017_09_10_1400.ruv - wera

        if row["sshkey_host"] == "localhost":
            rsync = [
                "rsync",
                "-ctdm",
                "--log-file=log/" + row["network"] + "_" + row["site"] + ".log",
                "--log-file-format='%n'",
                "--out-format='%n'",
                "--include='" + row["file_pattern"] + "'",
                "--files-from=" + findoutput,
                row["src_dir"],
                site_rsync_dir,
            ]

        else:
            rsync = [
                "rsync",
                "-ctdm",
                "--log-file=log/" + row["network"] + "_" + row["site"] + ".log",
                "--log-file-format='%n'",
                "--out-format='%n'",
                "--timeout=300",  # .ie, 5 minutes
                "--include='" + row["file_pattern"] + "'",
                "--files-from=" + findoutput,
                row["sshkey_host"] + ":" + row["src_dir"],
                site_rsync_dir,
            ]

        logging.debug(rsync)
        try:
            completed = subprocess.run(rsync, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as exc:
            logging.error("rsync failed: %s", exc.output.decode("ascii"))
            # remove all the files in --include file if there's an error
            with open(findoutput, "r") as f:
                logging.debug("findoutput: %s", findoutput)
                for cnt, line in enumerate(f):
                    logging.debug("Removing %s%s", site_rsync_dir, line)
                    path = os.path.join(site_rsync_dir, line.strip())
                    if os.path.exists(path):
                        os.remove(path)
        else:
            # If the ssh command returns something, could be an error, might be a welcome message
            if completed.stderr:
                # If it's an ssh error, it'll start with ssh.  Hopefully welcoming message won't
                # have ssh in it.
                if completed.stderr.decode("utf-8").startswith("ssh"):
                    logging.error("rsync failed(1): %s", completed.stderr.decode("ascii"))
                    # remove all the files in --include file if there's an error
                    with open(findoutput, "r") as f:
                        logging.debug("findoutput1: %s", findoutput)
                        for cnt, line in enumerate(f):
                            logging.debug("Removing1 %s%s", site_rsync_dir, line.strip())
                            path = os.path.join(site_rsync_dir, line)
                            if os.path.exists(path):
                                os.remove(path)
                    continue

        logging.debug("rsync completed")
        statetime = 0
        #
        # if all goes well, read the output from completed.decode('ascii')
        # and make sure each file passes QC and then copy the file to another
        # directory
        #
        for myfile in completed.stdout.decode("ascii").split("\n"):
            if "ruv" in myfile:
                logging.info("rsync found file: %s", myfile)
                myfile = myfile.replace("'", "")

                # validate the radial file
                rf = RadialFile(site_rsync_dir + myfile)

                # get file modification time and compare with state file last mod time
                statetime = rf.modificationTime + 60
                if not rf.modificationTime > row["state"]:
                    continue

                # if we set t0 or t1 check them with the file modification time
                if args.t0:
                    if rf.modificationTime < float(args.t0):
                        continue
                if args.t1:
                    if rf.modificationTime > float(args.t1):
                        continue

                # validate the inner metadata of the file
                if not rf.validFile():
                    logging.error("%s%s not valid", site_rsync_dir, myfile)
                    continue

                # if dryrun, we don't want to save the file to the holding directory
                if args.dryrun:
                    continue

                # Once the file has been validated, save the file into another holding directory,
                # while at the same time, changing the filename to reflect the current filenames.
                # This holding directory will be rsynced with the nodes.j
                # holding: /SIO/SDSC/m/RDL_m_SIO_SDSC_2018_06_14_1800.ruv
                # .create the new filename.
                p = re.compile("([0-9]{4})_([0-9]{2})_([0-9]{2})_([0-9]{4})")
                match = p.search(myfile)
                if not match:
                    logging.error("Unable to find suitable date/time in the filename %s" % myfile)
                else:
                    # make sure the holding directory exists
                    newdir = "%s/%s/%s/%s-%s/" % (row["node_rsync_dir"], row["network"], row["site"], match.group(1), match.group(2))
                    if not os.path.isdir(newdir):
                        logging.debug("Creating %s", newdir)
                        os.makedirs(newdir, exist_ok=True)

                    # RDL_m_SIO_SDBP_2018_06_04_2100.hfrss10lluv
                    # RDL_UH_KAK_2018_06_05_0700.hfrweralluv1.0
                    # RDL_USF_VEN_2018_06_05_1700.hfrweralluv1.0
                    logging.info("QC completed, copying file (%s) to %s", myfile, newdir)
                    if rf.isCodarFile():
                        newfile = "RDL_%s_%s_%s_%s_%s_%s_%s.ruv" % (row["patterntype"], row["network"], row["site"], match.group(1), match.group(2), match.group(3), match.group(4))
                    else:
                        newfile = "RDL_%s_%s_%s_%s_%s_%s.ruv" % (row["network"], row["site"], match.group(1), match.group(2), match.group(3), match.group(4))
                    try:
                        shutil.copy2(site_rsync_dir + myfile, newdir + newfile)
                    except EnvironmentError:
                        # IF copy fails delete the ruv file so it can get rsynced again and change statetime
                        logging.error("Unable to copy %s to %s%s" % (myfile, newdir, newfile))
                        os.remove(site_rsync_dir + myfile)
                        statetime = statetime - 120

        # if dryrun, we don't want to save the state to the DB
        if args.dryrun:
            continue
        # once we go through all the files, set the state time in
        # the database - if statetime is not zero (found a file)
        if statetime == 0:
            continue
        # if we are acquiring old files, we don't want to set statetime
        # - if t1 is defined, don't set the statetime.
        if args.t1:
            continue

        # if statetime isn't after the state time in the db, don't update it
        if statetime <= row["state"]:
            continue

        # .if everything validates correctly, set the state time variable to 1 minute behind the current time
        #  - try and update the main state database.
        #  - if that doesn't work, update the local one
        logging.debug("Updating state for site %s %s to %s", row["site"], row["patterntype"], str(statetime))

        try:
            db_state = pymysql.connect(
                user=config["state_database"]["user"],
                passwd=config["state_database"]["passwd"],
                host=config["state_database"]["host"],
                db=config["state_database"]["db"],
                port=int(config["state_database"]["port"]),
                ssl={"ssl": {"ca": config["state_database"]["ssl_ca"], "key": config["state_database"]["ssl_client_key"], "cert": config["state_database"]["ssl_client_cert"]}},
                cursorclass=pymysql.cursors.DictCursor,
            )
            with db_state.cursor() as state_cur:
                sql = "UPDATE site set state=%s WHERE network=%s AND site=%s and patterntype=%s"
                state_cur.execute(sql, (statetime, row["network"], row["site"], row["patterntype"]))
                logging.debug("Updated state time in master database")

        except pymysql.Error as e:
            code, msg = e.args
            logging.error("Unable to set state time in master database: %s", msg)

            try:
                with db.cursor() as state_cur:
                    logging.info("Attempting to set state time in local database")
                    sql = "UPDATE site set state=%s WHERE network=%s AND site=%s and patterntype=%s"
                    state_cur.execute(sql, (statetime, row["network"], row["site"], row["patterntype"]))
            except pymysql.Error as e:
                code, msg = e.args
                logging.error("Unable to set state time in local database: %s", msg)
            else:
                state_cur.close()
        else:
            state_cur.close()
            db_state.close()

cur.close()
db.close()
logging.info("Finished")

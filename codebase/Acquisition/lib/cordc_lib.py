"""



  Changes:
    2018-09-06 - Added is_number


"""
import subprocess
# import time


# . .. .. .. . ... . . . . .. .. .. . ... . . . . .. .. .. . ... . . . . .. .. .. . ... . . .
#  Returns a string if pattern matches in myfile
#
#   result = grep("RDL","SDBP.log")
#   if result:
#       for file in result.split('\n'):
#           print(file)
#   else:
#       print("no result")
#
def grep(pattern, myfile):

    grep = ["grep", "-E", pattern, myfile]
    try:
        completed = subprocess.check_output(grep, stderr=subprocess.STDOUT)
        return completed.decode('ascii')

    except subprocess.CalledProcessError as e:

        # scripps: e never used (exception not handled, just empty return)
        #
        # HF-Radar Network
        # - Scripps Institution of Oceanography
        # - Coastal Observing Research and Development Center

        return None


# . .. .. .. . ... . . . . .. .. .. . ... . . . . .. .. .. . ... . . . . .. .. .. . ... . . .
# retrieveBetweenTwoPatterns(p1,p2,f)
#
# - return a string of lines containing p1 and everything up to the last p2.
# - includes the first and last patterns.
# - DO NOT USE regular expressions in the patterns.
#
#
def retrieveBetweenTwoPatterns(pattern1, pattern2, myfile):

    cmd = ["awk", "/" + pattern1 + "/{flag=1};flag;/" + pattern2 + "/{exit}", myfile]
    try:
        completed = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return completed.decode('ascii')

    except subprocess.CalledProcessError as e:

        # scripps: e never used (exception not handled, just empty return)
        #
        # HF-Radar Network
        # - Scripps Institution of Oceanography
        # - Coastal Observing Research and Development Center

        return None


# . .. .. .. . ... . . . . .. .. .. . ... . . . . .. .. .. . ... . . . . .. .. .. . ... . . .
# is_number(v)
#
#   - check to see if a string is a number
#   - this could be better implemented using type(v)=='float'
#
#
def is_number(n):
    try:
        float(n)

    except ValueError:
        return False

    return True

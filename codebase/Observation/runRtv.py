"""

    RUNRTV Batch wrapper for processRtv

    runRtv(domain, resolution) is a wrapper for processRtv designed to
    capture any uncaught exceptions by processRtv itself. See processRtv
    for a full description of inputs.

    runRtv(..., configFunction, reprocessTimes, reprocessLock)
    optionally defines the configuration function and reprocessing
    parameters. The default configFunction is 'configureRtv' and
    reprocessLock defaults to true.

    All input checking is handled by processRtv.

    Full documentation and examples of usage in the batch context is
    available in the man(ual) page rtvproc(1).

    See also processRtv, rtvproc(7)

    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center

"""
import sys
import datetime
import processRtv


def runRtv(domain, resolution, configFunction=None, reprocessTimes=None, reprocessLock=True):

    # Define Anonymous functions

    # Current timestamp
    def ts(format):
        return datetime.datetime.now().strftime(format)

    # STDERR message in Logger format
    def errmsg(severity, msg):
        print(f"{ts('%Y/%m/%d %H:%M:%S')}\t{severity}\t\t{msg}", file=sys.stderr)

    # Config Option

    # Set default if needed
    defaultConfig = 'configureRtv'

    if configFunction is None:
        configFunction = defaultConfig

    # Reprocessing Option
    if reprocessTimes is not None and reprocessLock is None:
        reprocessLock = True

    # Main
    try:
        if reprocessTimes is not None:
            processRtv(domain, resolution, configFunction, reprocessTimes, reprocessLock)
        else:
            processRtv(domain, resolution, configFunction)
    except Exception as e:
        errmsg('error', str(e))



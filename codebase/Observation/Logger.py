"""

  LOGGER Logging class

    LOG = Logger(logFile) returns an object that has properties and methods for logging.

    Log messages can be written to both the command window and a log
    file.  All messages are filtered by the minimum severity which are
    defined independently for the command window and log file. Only
    messages at or above the minimum severity are written to the
    command window or log file.


    Severity levels in order of decreasing severity:
        off
            Not a severity level but, because it is higher than all
            other severity levels, it turns logging off when used as
            the minimum severity level.
        alert
            Notify operator of a condition that needs resolution such
            as bad or missing configuration settings or alarms
            reported by processing.
        error
            An error that prevents a process from completing and
            requires resulution.  Examples include poorly formatted
            data and unknown data formats.
        warning
            An error or anomaly that requires acknowledgement or
            resolution but only affects a portion of processing and
            does not prevent the process from completing. Examples
            include unknown data field formats, reported values that
            are out of range or failure to derive a data product.
        notice
            No error but indicates an unusual condition. No immediate
            action is required but it may indicate a problem.
        info
            Normal informational messages used for monitoring
            activity. No action needed.
        debug
            Debugging messages useful to developers but are not
            nomally enabled  during  normal operation due to their
            verbose and often cryptic nature.


    Times recorded during logging are in the system's timezone.

    Example:

        # Constructor
        LOG = Logger('/home/user/test.log');

        # Set minimum severity levels
        LOG.setLogLevel('info')
        LOG.setCmdWinLogLevel('error')

        # Log messages
        LOG.debug('debug test message')
        LOG.info('info test message')
        LOG.notice('notice test message')
        LOG.warning('warning test message')
        LOG.error('error test message')
        LOG.alert('alert test message')

        # Destroy the class
        LOG.delete
        clear LOG

    Properties (read-only):
        logFile        - File to log to
        logLevel       - Severity level at or above which messages are logged to file
        cmdWinLogLevel - Severity level at or above which messages are displayed to
                         the command window

    Methods:
        Logger
            Class constructor; defines logFile and default minimum
            severity of 'info' for logLevel and 'off' for
            cmdWinLogLevel.

        setLogLevel( level )
            Sets the minimum log level for file logging. Level is any
            defined severity level.  Use 'off' to disable logging to
            file.

        setCmdWinLogLevel( level )
            Sets the minimum log level for command window messages. Level is any
            defined severity level.  Use 'off' to disable command
            window messaging.

        debug   ( message )
        info    ( message )
        notice  ( message )
        warning ( message )
        error   ( message )
        alert   ( message )
            Write message (string) with corresponding
            method severity to the command window and log file.  Only
            messages with (method) severity at or above the minimum
            log or command window severity are actually written.


  .Mark Otero
   Scripps Institution of Oceanography
   Coastal Observing Research and Development Center


"""
import datetime


class Logger:

    DEBUG = 0
    INFO = 1
    NOTICE = 2
    WARNING = 3
    ERROR = 4
    ALERT = 5
    OFF = 6

    def __init__(self, logFile):
        if not isinstance(logFile, str):
            raise ValueError('logFile must be a string')

        self.logFile = logFile
        self.logLevel = ''
        self.cmdWinLogLevel = ''
        self.logLevelNum = None
        self.cmdWinLogLevelNum = None
        self.setLogLevel('info')
        self.setCmdWinLogLevel('off')

    def setLogLevel(self, level):
        level = level.lower()
        if level not in ['debug', 'info', 'notice', 'warning', 'error', 'alert', 'off']:
            raise ValueError('Invalid severity level')

        self.logLevel = level
        self.logLevelNum = getattr(self, level.upper())

    def setCmdWinLogLevel(self, level):
        level = level.lower()
        if level not in ['debug', 'info', 'notice', 'warning', 'error', 'alert', 'off']:
            raise ValueError('Invalid severity level')

        self.cmdWinLogLevel = level
        self.cmdWinLogLevelNum = getattr(self, level.upper())

    def debug(self, message):
        self.writeMessage(self.DEBUG, 'debug', message)

    def info(self, message):
        self.writeMessage(self.INFO, 'info', message)

    def notice(self, message):
        self.writeMessage(self.NOTICE, 'notice', message)

    def warning(self, message):
        self.writeMessage(self.WARNING, 'warning', message)

    def error(self, message):
        self.writeMessage(self.ERROR, 'error', message)

    def alert(self, message):
        self.writeMessage(self.ALERT, 'alert', message)

    def writeMessage(self, msgLevelNum, msgLevel, message):
        if self.cmdWinLogLevelNum > msgLevelNum and self.logLevelNum > msgLevelNum:
            return

        ts = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

        if self.cmdWinLogLevelNum <= msgLevelNum:
            print(f'{ts}\t{msgLevel}\t\t{message}')

        if self.logLevelNum <= msgLevelNum:
            try:
                with open(self.logFile, 'a') as f:
                    f.write(f'{ts}\t{msgLevel}\t\t{message}\n')
            except Exception as e:
                print(f'Error writing to log: {e}')

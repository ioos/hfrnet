"""



    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center


"""
import os
import subprocess
import re


class FileLock:
    def __init__(self, lockFile):
        if not isinstance(lockFile, str):
            raise ValueError('lockFile must be a string')

        if not os.name == 'posix':
            raise OSError('FileLock is only supported on UNIX platforms')

        self.lockFile = lockFile
        self.haveLock = False
        self.ourPid = str(os.getpid())
        self.ourCmd = ''
        self.lockPid = ''
        self.lockCmd = ''
        self.lockFileExists = False

        # Obtain the command associated with the PID
        pidCmdStr = subprocess.check_output(['ps', '-p', self.ourPid, '-o', 'pid=', '-o', 'cmd=']).decode('utf-8')
        pidCmdStr = pidCmdStr.strip()
        if not pidCmdStr:
            raise ValueError('Failed to find our PID ({})'.format(self.ourPid))
        else:
            pattern = r'\s?{}\s+(?P<cmd>.+)'.format(self.ourPid)
            captured = re.search(pattern, pidCmdStr)
            if not captured:
                raise ValueError('Failed to capture command from {}'.format(pidCmdStr))
            else:
                self.ourCmd = captured.group('cmd').strip()

    def lock(self):
        self.syncLock()

        if not self.haveLock and not self.lockFileExists:
            #
            # We're clear to create our own lock; lock isn't claimed and no lock file exists
            #
            # Open the lock file
            try:
                with open(self.lockFile, 'w') as f:
                    # Write the PID and command
                    f.write('{} {}\n'.format(self.ourPid, self.ourCmd))
            except IOError as e:
                raise IOError('Failed to open lock file: {}'.format(str(e)))

            # Re-sync to update properties
            self.syncLock()

    def unlock(self):
        self.syncLock()
        if not self.haveLock:
            print('Do not have lock, cannot unlock')
        else:
            os.remove(self.lockFile)

        # Re-sync
        self.syncLock()

    def __del__(self):
        self.syncLock()
        if self.haveLock:
            self.unlock()

    def syncLock(self):

        self.lockFileExists = os.path.exists(self.lockFile)
        if self.lockFileExists:
            # check existing locked process against system processes

            try:  # read the lock file
                with open(self.lockFile, 'r') as f:
                    lockStr = f.read()
            except IOError as e:
                raise IOError('Failed to read lock file: {}'.format(str(e)))

            # parse lock file for PID and command
            pattern = r'\s?(?P<pid>\d+)\s+(?P<cmd>.+)'
            captured = re.search(pattern, lockStr)
            if not captured:
                raise ValueError('Failed to parse lock file PID and command')
            else:
                self.lockPid = captured.group('pid').strip()
                self.lockCmd = captured.group('cmd').strip()

            # look for the lock PID among system processes
            try:
                pidCmdStr = subprocess.check_output(['ps', '-p', self.lockPid, '-o', 'pid=', '-o', 'cmd=']).decode('utf-8')
            except subprocess.CalledProcessError:
                noPidFound = True
            else:
                noPidFound = False

            if noPidFound:
                # Lock is stale if there is no matching PID
                print('Existing lock file is stale (no PID match), removing')
                os.remove(self.lockFile)
                self.lockFileExists = os.path.exists(self.lockFile)

                if self.lockFileExists:
                    raise OSError('Failed to remove stale lock file')

            elif not noPidFound:
                # Check the command associated with the PID and compare against lock command
                pattern = r'\s?{}\s+(?P<cmd>.+)'.format(self.lockPid)
                captured = re.search(pattern, pidCmdStr)
                if not captured:
                    raise ValueError('Failed to get command associated with the lock PID')
                else:
                    pidCmdMatch = captured.group('cmd').strip() == self.lockCmd

            if noPidFound or not pidCmdMatch:
                # Lock is stale if either there is no matching PID or the lock command doesn't match the system's command for the PID
                if noPidFound:
                    print('Existing lock file is stale (no PID match), removing')
                elif not pidCmdMatch:
                    print('Existing lock file is stale (PID command mis-match), removing')

                os.remove(self.lockFile)
                self.lockFileExists = os.path.exists(self.lockFile)

                if self.lockFileExists:
                    raise OSError('Failed to remove stale lock file')

        if self.lockFileExists:
            # Check object data is consistent with the existing lock file
            
            if self.haveLock and self.ourPid != self.lockPid:
                # Lock claimed but lock PID doesn't match our PID
                self.haveLock = False
                print('lost lock; lock file PID ({}) does not match our PID ({})'.format(self.lockPid, self.ourPid))

            elif not self.haveLock and self.ourPid == self.lockPid:
                # No lock but lock file exists and matches our PID
                self.haveLock = True

        else:
            # Lock file doesn't exist
            self.haveLock = False
            self.lockPid = ''
            self.lockCmd = ''

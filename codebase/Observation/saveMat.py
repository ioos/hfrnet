"""

  Save rtvproc data to MATLAB file

   Parameters:
    c (dict): Configuration structure
    t (any):  Timestamp
    X (dict): Data to be saved
    r (dict, optional): Radial data structure for rtv results

  Returns:
    tuple: (success, message) where success is a boolean and message is a string


"""
import os
import scipy.io as sio


def saveMat(c, t, X, r=None):

    # Initialize return values
    success = False
    message = ''

    # Basic input check for rtv
    if c['process']['name'].lower() == 'rtv' and r is None:
        message = 'RTV export requires radial data as input'
        return success, message

    # Determine if lta month sum data
    isLtaMonthSumData = False

    if c['process']['name'].lower() == 'lta' and \
       c['subprocess']['name'].lower() == 'month' and \
       'uAvg' not in X:
        isLtaMonthSumData = True

    # Define path based on process
    if isLtaMonthSumData:
        mypath = c['total']['msumdir']
    else:
        mypath = c['total']['mdir']

    # Build path, as needed
    if not os.path.isdir(mypath):
        try:
            os.makedirs(mypath)
        except OSError as e:
            message = f'Failed to make dir {mypath}: {str(e)}'
            return success, message

    # Save
    try:
        # Set path
        if isLtaMonthSumData:
            pathfile = c['total']['msumpathfile']
        else:
            pathfile = c['total']['mpathfile']

        # Drop fields that don't need to be saved or shouldn't be shared
        if c['process']['name'].lower() == 'rtv':
            if 'isnew' in r:
                del r['isnew']
            rmFields = ['log', 'lock', 'gridfile', 'grid', 'landfile', 'land', 'confdb',
                        'total', 'raddb', 'processes', 'stc', 'lta']
        elif c['process']['name'].lower() == 'stc':
            rmFields = ['log', 'lock', 'gridfile', 'landfile', 'confdb', 'total', 'raddb',
                        'processes', 'rtv', 'lta', 'ncid', 'getExternalMetadata',
                        'getExternalProcessMetadata']
        elif c['process']['name'].lower() == 'lta':
            rmFields = ['log', 'lock', 'gridfile', 'landfile', 'confdb', 'total', 'raddb',
                        'processes', 'rtv', 'stc', 'ncid', 'getExternalMetadata',
                        'getExternalProcessMetadata']

        for field in rmFields:
            if field in c:
                del c[field]

        # Save with native variable names
        if c['process']['name'].lower() == 'rtv':
            U = X
            sio.savemat(pathfile, {'c': c, 't': t, 'U': U, 'r': r})
        elif c['process']['name'].lower() == 'stc':
            tc = t
            A = X
            sio.savemat(pathfile, {'c': c, 'tc': tc, 'A': A})
        elif c['process']['name'].lower() == 'lta':
            if isLtaMonthSumData:
                S = X
                sio.savemat(pathfile, {'c': c, 't': t, 'S': S})
            else:
                A = X
                sio.savemat(pathfile, {'c': c, 't': t, 'A': A})

    except Exception as e:
        message = f'Error saving {pathfile}: {str(e)}'
        return success, message

    success = True
    return success, message

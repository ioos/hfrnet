import os
import numpy as np

def saveAscii(c, U):
    """
    SAVEASCII Export velocity data to ASCII file

    [ success, message ] = saveAscii( c, U ) saves rtvproc total velocity
    data products to a simple ASCII file consisting of 4 columns:
    latitude, longitude, u (eastward) velocity, and v (northward)
    velocity. The process name is obtained from the configuration
    structure's process field.  For rtv processing, the velocities are
    filtered by the rtv field's uwls_max_hdop_ascii value prior on export.

    The return values success and message will be true and empty,
    respectively, if there are no errors.  Otherwise, success will be
    false and any response will be provided in message.

    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center
    """

    # Initialize return values
    success = False
    message = ''

    # Build save dir, as needed
    if not os.path.isdir(c['total']['asciidir']):
        try:
            os.makedirs(c['total']['asciidir'])
        except OSError as e:
            message = f"Failed to make dir {c['total']['asciidir']}: {e.strerror}"
            return success, message

    # Save
    try:
        # Filter velocities by process type
        process_name = c['process']['name']
        if process_name == 'rtv':
            f = U['hdop'] <= c['rtv']['uwls_max_hdop_ascii']
            D = np.array([U['lat'][f], U['lon'][f], U['u'][f], U['v'][f]]).T
        elif process_name in ['stc', 'lta']:
            f = ~np.isnan(U['uAvg'])
            D = np.array([U['lat'][f], U['lon'][f], U['uAvg'][f], U['vAvg'][f]]).T
        else:
            raise ValueError(f"Velocity filtering is undefined for process '{process_name}'")

        # Write to file
        with open(c['total']['asciipathfile'], 'w') as fid:
            np.savetxt(fid, D, fmt='%8.4f %9.4f %7.0f %7.0f')

    except Exception as e:
        message = f"Error saving {c['total']['asciipathfile']}: {str(e)}"
        return success, message

    success = True
    return success, message



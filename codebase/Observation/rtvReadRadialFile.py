"""

   RTVREADRADIALFILE Read lluv radial file to structure

   r = rtvReadRadialFile(s) reads the radial file defined in the
   structure and returns a structure containing radial data used during RTV
   processing. The radial file format must be lluv. The radar location is
   used to compute speed and heading fields from radial velocity if they
   aren't directly available in the file.

   Input:
      s['fullfile'] - radial file name (including the full path if not on the MATLAB path)
      s['lat']      - radar latitude (deg N)
      s['lon']      - radar longitude (deg E)

   Output:
      r - Dictionary of radial velocity data including the fields:
            latitude
            longitude
            speed
            heading
            range (if available)
            vflag (if available)

    The heading is returned in polar convention (counterclockwise from the
    +x axis). The range and vflag fields are only returned if they're
    available in the file.


"""
import os
import re
import numpy as np
from geopy.distance import geodesic
from collections import defaultdict


def rtvReadRadialFile(s):

    # Check file exists
    if not os.path.isfile(s['fullfile']):
        raise FileNotFoundError(f"{s['fullfile']} not found")

    # Get LLUV Table Column Names
    with open(s['fullfile'], 'r') as fid:
        tableType = ''
        columnIndex = {}
        while True:
            tline = fid.readline()
            if not tline:
                break

            # Look for column names if the current table is the right type
            if tableType == 'LLUV':
                m = re.findall(r'^%TableColumnTypes:(\s*\w+\s*)+', tline)
                if m:
                    m = m[0].strip().split()
                    for i, col in enumerate(m):
                        columnIndex[col] = i
                    break
            else:
                m = re.findall(r'^%TableType:\s*LLUV', tline)
                if m:
                    tableType = 'LLUV'

    # Check we got required column names
    if not columnIndex:
        raise ValueError('No column names were found')
    elif 'LOND' not in columnIndex:
        raise ValueError('Longitude column (LOND) not found')
    elif 'LATD' not in columnIndex:
        raise ValueError('Latitude column (LATD) not found')
    elif 'HEAD' not in columnIndex:
        print('Warning: Radial heading column (HEAD) not found')
    elif 'VELO' not in columnIndex:
        print('Warning: Radial velocity column (VELO) not found')
    elif 'RNGE' not in columnIndex:
        print('Warning: Radial range column (RNGE) not found')

    # Load data
    d = np.loadtxt(s['fullfile'])

    if d.size == 0:
        raise ValueError('Load function returned an empty array. No data in radial file?')

    r = defaultdict(list)

    # Radial location
    r['latitude'] = d[:, columnIndex['LATD']]
    r['longitude'] = d[:, columnIndex['LOND']]

    # Radial heading (toward origin)
    if 'HEAD' in columnIndex:
        # Convert deg CW from N to deg CCW from E
        r['heading'] = (90 - d[:, columnIndex['HEAD']]) % 360
    else:
        # Compute bearing from each radial to the origin
        r['heading'] = []
        for lat, lon in zip(r['latitude'], r['longitude']):
            az = geodesic((lat, lon), (s['lat'], s['lon'])).initial
            r['heading'].append((90 - az) % 360)

    # Radial speed
    if 'VELO' in columnIndex:
        r['speed'] = d[:, columnIndex['VELO']]
    elif 'VELU' in columnIndex and 'VELV' in columnIndex:
        # Convert radial vector to polar coords (speed and bearing)
        rdir, rspd = np.arctan2(d[:, columnIndex['VELV']], d[:, columnIndex['VELU']]), np.hypot(d[:, columnIndex['VELU']], d[:, columnIndex['VELV']])
        rdir = np.degrees(rdir)
        dd = np.abs(r['heading'] - rdir) % 360
        mask = dd > 10
        rspd[mask] = -rspd[mask]
        r['speed'] = rspd
    else:
        raise ValueError('Radial velocity components (VELU & VELV) not found')

    # Radial range (from origin)
    if 'RNGE' in columnIndex:
        r['range'] = d[:, columnIndex['RNGE']]

    # Radial flags
    if 'VFLG' in columnIndex:
        r['vflag'] = d[:, columnIndex['VFLG']]

    return r



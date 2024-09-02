"""

  uwlsTotal(rSpeed, rHeading)

    description:
      computes a total velocity from radials using unweighted least-squares

    parameters:
     rSpeed   (np.ndarray): column vector (n* x 1) of radial velocity magnitude
     rHeading (np.ndarray): column vector (n* x 1) of radial velocity heading in
                            degrees counterclockwise from +x (east)

    returns:
      u    (float): eastward total velocity
      v    (float): northward total velocity
      dopx (float): eastward dilution of precision
      dopy (float): northward dilution of precision
      hdop (float): horizontal dilution of precision

    ..all output values are scalars and the units of eastward and northward
      velocity are the same as the units for rSpeed.


    Radial velocities are related to the total velocity by projection of
    the eastward and northward components of the total velocity onto the
    radial heading:

        rSpeed = u*cosd(rHeading) + v*sind(rHeading)

    and in matrix form as

        rSpeed = X*b

    where

        X = [ cosd(rHeading) sind(rHeading) ]
        b = [ u; v ]


    The unweighted least squares solution for b is given by

        b = inv( X'*X ) * X' * rSpeed

    The geometric portion of the covariance matrix for b is

        C = inv( X'*X )

    which provides the dilution of precision along the diagonal where

        dopx = sqrt( C(1,1) )
        dopy = sqrt( C(2,2) )
        hdop = sqrt( C(1,1) + C(2,2) )


"""
import numpy as np


def uwlsTotal(rSpeed, rHeading):

    X = np.zeros((len(rHeading), 2))
    X[:, 0] = np.cos(np.deg2rad(rHeading))
    X[:, 1] = np.sin(np.deg2rad(rHeading))

    C = np.linalg.inv(X.T @ X)

    dopx = np.sqrt(C[0, 0])
    dopy = np.sqrt(C[1, 1])
    hdop = np.sqrt(C[0, 0] + C[1, 1])

    b = C @ X.T @ rSpeed

    u = b[0]
    v = b[1]

    return u, v, dopx, dopy, hdop

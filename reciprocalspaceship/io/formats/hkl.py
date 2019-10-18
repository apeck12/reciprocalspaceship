import pandas as pd
import gemmi
from reciprocalspaceship import Crystal

def read(hklfile, a=None, b=None, c=None, alpha=None, beta=None,
         gamma=None, sg=None):
    """
    Initialize attributes and populate the crystal object with data from
    a HKL file of reflections. This is the output format used by 
    Precognition when processing Laue diffraction data.

    Parameters
    ----------
    hklfile : str or file
        name of an hkl file or a file object
    a : float
        edge length, a, of the unit cell
    b : float
        edge length, b, of the unit cell
    c : float
        edge length, c, of the unit cell
    alpha : float
        interaxial angle, alpha, of the unit cell
    beta : float
        interaxial angle, beta, of the unit cell
    gamma : float
        interaxial angle, gamma, of the unit cell
    sg : str or int
        If int, this should specify the space group number. If str, 
        this should be a space group symbol
    """
    # Read data from HKL file
    if hklfile.endswith(".hkl"):
        usecols = [0, 1, 2, 3, 4, 5, 6]
        F = pd.read_csv(hklfile, header=None, delim_whitespace=True,
                        names=["H", "K", "L", "F+", "SigF+", "F-", "SigF-"],
                        usecols=usecols)
    elif hklfile.endswith("*.ii"):
        usecols = range(10)
        F = pd.read_csv(hklfile, header=None, delim_whitespace=True,
                        names=["H", "K", "L", "Multiplicity", "X", "Y",
                               "Resolution", "Wavelength", "I", "SigI"],
                        usecols=usecols)

    crystal = Crystal()

    for k,v in F.items():
        crystal[k] = v
    crystal.set_index(["H", "K", "L"], inplace=True)

    # Set Crystal attributes
    if (a and b and c and alpha and beta and gamma):
        crystal.cell = gemmi.UnitCell(a, b, c, alpha, beta, gamma)
    if sg:
        crystal.spacegroup = gemmi.SpaceGroup(sg)
        
    return crystal
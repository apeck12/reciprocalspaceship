import numpy as np
from gemmi import SpaceGroup,GroupOps
import reciprocalspaceship as rs

def to_structurefactor(sfamps, phases):
    """
    Convert structure factor amplitude and phase to complex structure
    factors

    Parameters
    ----------
    sfamps : DataSeries or array-like
        Structure factor amplitudes
    phases : DataSeries or array-like
        Phases corresponding to structure factors

    Returns
    -------
    sfs : np.ndarray
        Array of complex-valued structure factors
    """
    if isinstance(sfamps, rs.DataSeries):
        sfamps = sfamps.to_numpy()
    if isinstance(phases, rs.DataSeries):
        phases = phases.to_numpy()
    return sfamps*np.exp(1j*np.deg2rad(phases))

def from_structurefactor(sfs):
    """
    Convert complex structure factors into structure factor amplitudes
    and phases

    Parameters
    ----------
    sfs : np.ndarray
        array of complex structure factors to be converted

    Returns
    -------
    (sf, phase) : tuple of DataSeries
        Tuple of DataSeries for the structure factor amplitudes and 
        phases corresponding to the provided complex structure factors
    """
    sf = rs.DataSeries(np.abs(sfs), name="F").astype("SFAmplitude")
    phase = rs.DataSeries(np.angle(sfs, deg=True), name="Phi").astype("Phase")
    return sf, phase

_L = {
    "P" : 1,
    "A" : 2,
    "B" : 2,
    "C" : 2,
    "I" : 2,
    "F" : 4,
    "R" : 3,
}

def compute_structurefactor_multiplicity(H, sg):
    """
    Parameters
    ----------
    H : array
        n x 3 array of Miller indices
    spacegroup : gemmi.SpaceGroup, gemmi.GroupOps
        The space group to identify the asymmetric unit
    Returns
    -------
    epsilon : array
        an array of length n containing the multiplicity
        of each hkl.
    """
    if isinstance(sg, SpaceGroup):
        group_ops = sg.operations()
    elif isinstance(sg, GroupOps):
        group_ops = sg
    else:
        raise ValueError(f"gemmi.SpaceGroup or gemmi.GroupOps expected for parameter sg. "
                         f"Received object of type: ({type(sg)}) instead.")

    is_centric = group_ops.is_centric()
    L = _L[group_ops.find_centering()]
    L = L*(1 + is_centric)
    eps = np.zeros(len(H))
    for op in group_ops:
        h = rs.utils.apply_to_hkl(H, op)
        if is_centric:
            eps += np.all(h==H, 1) | np.all(h==-H, 1)
        else:
            eps += np.all(h==H, 1) 
    return eps/L

def is_centric(H, spacegroup):
    """
    Determine if structure factors are centric in a given spacegroup
    Parameters
    ----------
    H : array
        n x 3 array of Miller indices
    spacegroup : gemmi.SpaceGroup, gemmi.GroupOps
        The space group in which to classify centrics
    Returns
    -------
    centric : array
        Boolean arreay with len(centric) == np.shape(H)[0] == n
    """
    if isinstance(spacegroup, SpaceGroup):
        group_ops = spacegroup.operations()
    elif isinstance(spacegroup, GroupOps):
        group_ops = spacegroup
    else:
        raise ValueError(f"gemmi.SpaceGroup or gemmi.GroupOps expected for parameter sg. "
                         f"Received object of type: ({type(sg)}) instead.")

    hkl,inverse = np.unique(H, axis=0, return_inverse=True)
    centric = np.zeros(len(hkl), dtype=bool)
    for op in group_ops:
        newhkl = rs.utils.apply_to_hkl(hkl, op)
        centric = np.all(newhkl == -hkl, 1) | centric
    return centric[inverse]


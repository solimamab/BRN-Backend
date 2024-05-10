import nibabel as nib
import numpy as np

brodmann_to_mni = {
    1: (-40, -27, 47),
    2: (-40, -27, 47),
    3: (-40, -27, 47),
    4: (-36, -19, 48),
    5: (-14, -33, 48),
    6: (-28, -2, 52),
    7: (-18, -61, 55),
    8: (-23, 24, 44),
    9: (-39, 34, 37),
    10: (-23, 55, 4),
    11: (-11, 38, -19),
    12: (-11, 38, -19),
    13: (-42, 4, -1),
    16: (-42, 4, -1),
    17: (-11, -81, 7),
    18: (-19, -92, 2),
    19: (-45, -75, 11),
    20: (-47, -14, -34),
    21: (-59, -25, -13),
    22: (-57, -20, 1),
    23: (-10, -45, 24),
    24: (-5, 1, 32),
    25: (-5, 17, -13), 
    30: (-12, -43, 8),
    31: (-8, -49, 38),
    32: (-5, 39, 20),
    34: (-28, 3, -17),
    36: (-26, -20, -22),
    37: (-47, -52, -12),
    38: (-43, 13, -30),
    39: (-46, -60, 33),
    40: (-53, -32, 33),
    41: (-52, -19, 7),
    44: (-48, 13, 17),
    45: (-47, 27, 6),
    46: (-46, 38, 8),
    47: (-40, 31, -13),
}

def load_atlas(atlas_path):
    """
    Load the atlas NIfTI file.
    """
    return nib.load(atlas_path)

def mni_to_voxel(coords, affine):
    """
    Convert MNI coordinates to voxel coordinates.
    """
    return nib.affines.apply_affine(np.linalg.inv(affine), coords)

def find_closest_parcel(atlas, coords):
    """
    Find the closest parcel to the given MNI coordinates.
    """
    # Convert MNI coordinates to voxel coordinates
    voxel_coords = mni_to_voxel(np.array(coords), atlas.affine).astype(int)
    
    # Extract the parcel index at the voxel coordinates
    try:
        parcel_index = atlas.get_fdata()[tuple(voxel_coords)]
    except IndexError:
        print("Coordinates are out of the atlas bounds.")
        return None
    
    if parcel_index == 0:
        print("No parcel found directly at these coordinates, searching nearby...")
        return search_nearby_voxels(atlas, voxel_coords)
    else:
        return int(parcel_index)

def search_nearby_voxels(atlas, voxel_coords, search_radius=3):
    """
    Search for the nearest non-zero parcel within a cube around the initial voxel.
    """
    atlas_data = atlas.get_fdata()
    shape = atlas_data.shape
    search_range = range(-search_radius, search_radius+1)
    for i in search_range:
        for j in search_range:
            for k in search_range:
                x, y, z = voxel_coords + np.array([i, j, k])
                if 0 <= x < shape[0] and 0 <= y < shape[1] and 0 <= z < shape[2]:
                    candidate_parcel = atlas_data[x, y, z]
                    if candidate_parcel != 0:
                        return int(candidate_parcel)
    print("No parcels found within search radius.")
    return None

def get_mni_from_brodmann(brodmann_area):
    """
    Converts Brodmann Area to MNI coordinates.
    """
    try:
        return brodmann_to_mni[brodmann_area]
    except KeyError:
        logger.error(f"Brodmann Area {brodmann_area} not found in mapping.")
        return 0, 0, 0

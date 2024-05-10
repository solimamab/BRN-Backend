import nibabel as nib
import numpy as np

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
    voxel_coords = mni_to_voxel(np.array(coords), atlas.affine).astype(int)

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
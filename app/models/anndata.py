"""
Anndata: represents the Anndata files for a dataset.

Currently, Anndata assumes HuBMAP file paths.
"""
import anndata as ad
import numpy as np

class Anndata:
    def __init__(self, dataset_uuid:str):
        self.dataset_uuid = dataset_uuid
        # Vitessce data elements
        self.adatas = []
        self.adata_zarr_paths = []

        # Get Anndata
        self.adatas = []
        self.adatas_zarr_paths = []

        self.adatas.append(ad.read_h5ad('datasets/' + self.dataset_uuid + '/secondary_analysis.h5ad'))
        self.adata_zarr_paths.append('datasets/' + self.dataset_uuiduuid + '/hubmap_ui/anndata-zarr/secondary_analysis.zarr')
        num_cells = np.sum([adata.n_obs for adata in self.adatas])
        print(f"Number of total cells: {num_cells}")
"""
spatialquery_vitessce.py
SpatialQuery/Vitessce integration class.
"""
import warnings
import pandas as pd
import numpy as np
import anndata as ad
import zarr
from zarr.storage import LocalStore
from flask import abort
import os

from SpatialQuery.spatial_query import spatial_query

from vitessce import (
    VitessceConfig,
    AnnDataWrapper,
    ViewType as vt,
    CoordinationType as ct,
    CoordinationLevel as CL,
)
from vitessce.widget_plugins import SpatialQueryPlugin

warnings.filterwarnings("ignore")
pd.set_option('display.max_colwidth', 1000)
pd.set_option('display.max_columns', 500)

class SpatialQueryVitessceManager:

    def __init__(self, absolute_file_path:str):

        """

        :param absolute_file_path: absolute file path to a set of secondary analysis files

        """

        spatial_key = 'X_spatial'
        label_key = 'predicted_label'

        """
        The Anndata object uses arrays for data related to anndata files.
        For the purposes of Single FOV analysis, there will be only
        one file.
        """

        print('Loading secondary analysis data')

        # Development: emulate PSC file system on local machine.
        adata_path = '/Users/jas971/spatial-query/secondary_analysis.h5ad'
        #adata_path = f'{absolute_file_path}/secondary_analysis.h5ad'
        if not os.path.exists(adata_path):
            abort(404,f'The secondary_analysis.h5ad file was not found in path {adata_path}.')
        self.adata = ad.read_h5ad(adata_path)

        # Development: emulate PSC file system on local machine.
        #self.zarr_paths = f'{absolute_file_path}/secondary_analysis.zarr'
        self.zarr_paths = '/Users/jas971/spatial-query/secondary-analysis.zarr'
        if not os.path.exists(self.zarr_paths):
            abort(404,f'The secondary_analysis.zarr directory was not found in path {self.zarr_paths}.')

        self.spatial_key = 'X_spatial'
        self.label_key = 'predicted_label'
        self.feature_name = 'hugo_symbol'

        print('Calling spatial_query')
        self.single_sp = spatial_query(
            adata=self.adata,
            dataset="single-fov",
            spatial_key=self.spatial_key,
            label_key=self.label_key,
            leaf_size=10,
            build_gene_index=False,
            feature_name=self.feature_name,
            if_lognorm=True,
            if_normalize_spatial_coord=True,
        )

    def find_fp_knn(self, celltype: str)->pd.DataFrame:
        """
        Wrapper for the find_fp_kpp function of the SpatialQuery API

        """
        print('central cell type', celltype)
        fp_knn = self.single_sp.find_fp_knn(
            ct=celltype,
            k=30,
            min_support=0.7
        )

        return fp_knn

    def get_vitessce_widget(self):
        """
        Does the following:
        1. Initializes a SpatialQuery Vitessce plugin
        2. Configures Vitessce
        3. Initializes a SpatialQuery Vitessce widget
        4. Passes the plugin to the widget
        :return: SpatialQuery Vitessce widget object

        """

        print('Initializing SpatialQuery Vitessce plugin')
        plugin = SpatialQueryPlugin(self.adata,
                                         spatial_key=self.spatial_key,
                                         label_key=self.label_key,
                                         feature_name=self.feature_name)

        vc = VitessceConfig(schema_version="1.0.16", name="Spatial-Query")

        """
        Dev note: the original code called the function with 
        adata_store=zarr.DirectoryStore(adata_zarr_paths[0]).
        DirectoryStore is no longer an attribute of zarr. 
        Based on a discussion in the zarr repo, I changed to 
        zarr.storage.LocalStore, which worked.
        """

        dataset = vc.add_dataset("Query results").add_object(AnnDataWrapper(
            adata_store=zarr.storage.LocalStore(self.zarr_paths),
            obs_feature_matrix_path="X",
            obs_set_paths=[f"obs/{self.label_key}"],
            obs_set_names=["Cell Type"],
            obs_spots_path=f"obsm/{self.spatial_key}",
            feature_labels_path="var/hugo_symbol",
            coordination_values={
                "featureLabelsType": "Gene symbol",
            }
        ))

        spatial_view = vc.add_view("spatialBeta", dataset=dataset)
        lc_view = vc.add_view("layerControllerBeta", dataset=dataset)
        sets_view = vc.add_view("obsSets", dataset=dataset)
        features_view = vc.add_view("featureList", dataset=dataset)
        sq_view = vc.add_view("spatialQuery", dataset=dataset)

        obs_set_selection_scope, = vc.add_coordination("obsSetSelection", )
        obs_set_selection_scope.set_value(None)

        sets_view.use_coordination(obs_set_selection_scope)
        sq_view.use_coordination(obs_set_selection_scope)
        spatial_view.use_coordination(obs_set_selection_scope)
        features_view.use_coordination(obs_set_selection_scope)

        vc.link_views([spatial_view, lc_view, sets_view, features_view],
                      ["additionalObsSets", "obsSetColor"],
                      [plugin.additional_obs_sets, plugin.obs_set_color]
                      )
        vc.link_views_by_dict([spatial_view, lc_view], {
            "spotLayer": CL([
                {
                    "obsType": "cell",
                    "spatialSpotRadius": 15,
                },
            ])
        })

        vc.layout((spatial_view | (lc_view / features_view)) / (sets_view | sq_view))

        config_json = vc.to_dict(base_url="http://localhost:8000")
        return config_json



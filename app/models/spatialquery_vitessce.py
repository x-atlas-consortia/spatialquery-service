"""
spatialquery_vitessce.py
SpatialQuery/Vitessce integration class.
"""
import warnings
import pandas as pd
import zarr
from zarr.storage import LocalStore

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

from .anndata import Anndata

class SpatialQueryVitessce:

    def __init__(self, anndata: Anndata, celltype: str):

        """

        :param anndata: Anndata object of data products for a dataset
        :param celltype: preferred term for the cell type used as an anchor motif
        """
        self.anndata = anndata
        self.celltype = celltype

        spatial_key = 'X_spatial'
        label_key = 'predicted_label'

        """
        The Anndata object uses arrays for data related to anndata files.
        For the purposes of Single FOV analysis, there will be only
        one file.
        """

        self.adata = self.anndata.adatas[0]

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


    def find_fp_knn(self)->pd.DataFrame:
        """
        Wrapper for the find_fp_kpp function of the SpatialQuery API

        """
        central_ct = self.celltype
        print('central cell type', central_ct)
        fp_knn = self.single_sp.find_fp_knn(
            ct=central_ct,
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

        """
                Initialize SpatialQuery Vitessce plugin
                """
        print('Initializing SpatialQuery Vitessce plugin')
        self.plugin = SpatialQueryPlugin(self.adata,
                                         spatial_key=self.spatial_key,
                                         label_key=self.label_key,
                                         feature_name=self.feature_name)

        vc = VitessceConfig(schema_version="1.0.16", name="Spatial-Query")
        dataset = vc.add_dataset("Query results").add_object(AnnDataWrapper(
            adata_store=zarr.storage.LocalStore(self.anndata.adata_zarr_paths[0]),
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
                      [self.plugin.additional_obs_sets, self.plugin.obs_set_color]
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



# SpatialQuery Service
# Background

## Project Milestone
[Link](https://github.com/hubmapconsortium/pitt-milestones/issues/86)

## SpatialQuery documentation
[Link](https://spatialquery.readthedocs.io/en/latest/)

# Objectives

The HuBMAP Data Portal provides access to datasets containing spatially 
resolved transcriptomics data from modalities including 
Slide-seq, Visium, Xenium, CODEX, PhenoCycler, MIBI, and CellDIVE. 

These datasets can be analyzed by the SpatialQuery package to 
+ identify cell-type spatial co-occurrence patterns (motifs)
+ perform motif enrichment analysis
+ conduct motif-associated molecular analysis within spatial neighborhoods.

[SpatialQuery](https://github.com/ShaokunAn/Spatial-Query/blob/2d0f76e5390b81467758932efb1b6103fa220be1/README.md) is a class-based package that is initialized by loading the AnnData file (.h5ad) for a specified HuBMAP dataset. SpatialQuery offers parameterized analysis functions that return Pandas DataFrames of information related to the dataset.

# Use case
The prototype use case for SpatialQuery service in the HuBMAP Data Portal is the Vitessce visualization of the Single Field Of View (FOV) analysis of a spatially resolved transcriptomics dataset. 

## Inputs
+ The end user selects a spatially resolved dataset from the Data Portal.
+ The end user specifies a cell type of interest (or “central cell type”) that the FOV analysis uses as an “anchor” for motif enrichment.

## Outputs
The Data Portal displays a separate Vitessce visualization of the SpatialQuery FOV results for the selected dataset and cell type.

# Prototype integration/Tutorial

A prototype using the SpatialQuery API is available as a Jupyter Notebook in a HuBMAP Workspace. 

To launch the workspace,
1. Log in to the HuBMAP Data Portal with a user with Workspace privileges.
2. Select the dataset with HuBMAP ID HBM847.GZGD.668.
3. In the far right menu of the dataset view, select Workspace.
4. Specify the SpatialQuery environment.

The notebook is the basis for [Tutorial 1](https://spatialquery.readthedocs.io/en/latest/tutorials/tutorial_1.html) in the SpatialQuery documentation site.

As of August 2026, the notebook no longer works.

---
# SpatialQuery Service integration
The SpatialQuery service will support integration with 
* the appropriate environment (HuBMAP or SenNet) API endpoints (i.e., in entity-api, uuid-api, ingest-api, etc.)
* SpatialQuery API endpoints
* calls to the SpatialQuery Vitessce Widget

The service will reside in a component that is common to both the HuBMAP and SenNet environments.

# Service architecture
The SpatialQuery service will be a Flask application that manages calls to the various services and APIs.

# Service requirements
1. The service will use the environment-appropriate api to obtain the UUID of spatially resolved datasets.
2. The service will encapsulate calls to the SpatialQuery API and SpatialQuery Vitessce widget.

# Service endpoints
## /get_dataset_uuid
### parameters
#### hmid
* in: path
* format: case-insensitive string corresponding to the HuBMAP ID of a spatially resolved dataset
* example: HBM847.GZGD.668
### calls
* environment entity-api
### response
#### uuids
array of uuids corresponding to the Anndata (HD5) files associated with the dataset.

## /get_spatialquery_single_fov

# Example code: from Jupyter notebook

The following code is taken from the example workspace Jupyter notebook. 
Python code from the various blocks in the notebook was consolidated into a single block of code. 

The inputs for the code block are:
A list of dataset UUIDs
The preferred term for an anchor cell type

The output of the code block is an invocation of Vitessce.
/spatialquery/uuid/celltype-id

```azure
import requests
import json
import os
import warnings

import numpy as np
import pandas as pd
import anndata as ad
import zarr

from tqdm import tqdm

from hubmap_template_helper import compatibility as hth_comp

from SpatialQuery.spatial_query import spatial_query
from SpatialQuery.spatial_query_multiple_fov import spatial_query_multi

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


# linked datasets
uuids = ['a1d17fdd270a69c813b872a927dfa5f3']

adatas = []
adata_zarr_paths = [] # for vitessce
for uuid in tqdm(uuids):
    adatas.append(ad.read_h5ad('datasets/' + uuid + '/secondary_analysis.h5ad'))
    adata_zarr_paths.append('datasets/' + uuid + '/hubmap_ui/anndata-zarr/secondary_analysis.zarr')

search_api = 'https://search.api.hubmapconsortium.org/v3/portal/search'

accepted_assay_display_names = ["Slide-seq [Salmon]"]

print(len(uuids))
uuids = hth_comp.check_template_compatibility(uuids, search_api=search_api, accepted_assay_display_names=accepted_assay_display_names)
print(len(uuids))

spatial_key = 'X_spatial'
label_key = 'predicted_label'

adata = adatas[0]

single_sp = spatial_query(
    adata=adata,
    dataset="single-fov",
    spatial_key=spatial_key,
    label_key=label_key,
    leaf_size=10
)

#CL_id = 0000653
central_ct = 'podocyte'
fp_knn = single_sp.find_fp_knn(
    ct=central_ct,
    k=30,
    min_support=0.7
)
fp_knn

plugin = SpatialQueryPlugin(adata, spatial_key=spatial_key, label_key=label_key)

vc = VitessceConfig(schema_version="1.0.16", name="Spatial-Query")
dataset = vc.add_dataset("Query results").add_object(AnnDataWrapper(
    adata_store=zarr.DirectoryStore(adata_zarr_paths[0]),
    obs_feature_matrix_path="X",
    obs_set_paths=[f"obs/{label_key}"],
    obs_set_names=["Cell Type"],
    obs_spots_path=f"obsm/{spatial_key}",
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

obs_set_selection_scope, = vc.add_coordination("obsSetSelection",)
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

vc.layout((spatial_view | (lc_view / features_view)) / (sets_view | sq_view));

vw = vc.widget(height=900, plugins=[plugin], remount_on_uid_change=False)
vw

```
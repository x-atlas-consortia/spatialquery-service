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
* the hubmap-template-helper library's check_template_compatibility function:

```
uuids = hth_comp.check_template_compatibility(uuids, search_api=search_api, accepted_assay_display_names=accepted_assay_display_names)
```

### response
#### uuids
array of uuids corresponding to the Anndata (HD5) files associated with the dataset.

## /get_spatialquery_single_fov
### parameters
##### cell-type
* in: path
* format: string corresponding to the preferred term for the cell type to be used as the anchor for motif enrichment
* example: podocyte
##### uuid
* in: path
* format: uuid for the spatially resolved dataset to use for Single FOV analysis
### pseudocode
Based on the non-functioning Jupyter notebook, tasks include:
1. Load spatial transcriptomics data for the UUID, using relative paths. 
```azure
adatas = []
adata_zarr_paths = [] # for vitessce
for uuid in tqdm(uuids):
    adatas.append(ad.read_h5ad('datasets/' + uuid + '/secondary_analysis.h5ad'))
    adata_zarr_paths.append('datasets/' + uuid + '/hubmap_ui/anndata-zarr/secondary_analysis.zarr')
```

2. Initialize SpatialQuery Single FOV analysis

The process begins with the initialization of a SpatialQuery object, which involves constructing a KD-tree using spatial location data and storing labels for each spot.

Use an annotated AnnData object loaded from "secondary_analysis.h5ad". The key components for initialization are:

* Cell annotations: Stored in AnnData.obs, accessed using the label_key parameter.
* Spatial locations: Stored in AnnData.obsm, accessed using the spatial_key parameter.
* Dataset identifier: An optional dataset parameter can be provided to uniquely name each FOV.
```azure
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
```

3. Initialize Vitessce SpatialQuery plugin
Interactive visualization with Vitessce currently only supports the single-FOV analysis case. 
Construct a SpatialQueryPlugin for Vitessce, which we pass when calling vc.widget(). 
This plugin adds the "Spatial Query Manager" view, facilitating interactive modification of 
query parameters and query execution via a graphical interface.

The values of **adata**, **spatial_key**, and **labe_key** are set in the intialization of SpatialQuery.
```azure
plugin = SpatialQueryPlugin(adata, spatial_key=spatial_key, label_key=label_key)
```
4. Configure Vitessce with our dataset and views of interest. Initialize cell type colors so they are used consistently for both cell type annotations and cell types that appear in SpatialQuery results.
```azure
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
```

5. Finally, render the Vitessce widget and pass the SpatialQueryPlugin instance.
```azure
vw = vc.widget(height=900, plugins=[plugin], remount_on_uid_change=False)
vw
```
### response
Vitessce interaction

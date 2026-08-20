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

# PROTOTYPES

## Jupyter notebook

A prototype using the SpatialQuery API is available as a Jupyter Notebook in a HuBMAP Workspace. 

To launch the workspace,
1. Log in to the HuBMAP Data Portal with a user with Workspace privileges.
2. Select the dataset with HuBMAP ID HBM847.GZGD.668.
3. In the far right menu of the dataset view, select Workspace.
4. Specify the Python kernel (at least 3.10) and the SpatialQuery template.

The notebook is related to [Tutorial 1](https://spatialquery.readthedocs.io/en/latest/tutorials/tutorial_1.html) in the SpatialQuery documentation site.

## Python prototype application
The _app_ directory of this repository contains a Web application that performs Single FOV analysis on a dataset and 
provides a JSON of Vitessce widget information.

The application:
1. Displays a web page with a form that allows the user the specify the consortium, dataset id, and cell type to use as anchor motif.
2. Authenticates to the appropriate Globus consortium.
3. Loads H5AD and Zarr files for the dataset from a local store.
4. Performs Single FOV analysis on the specified dataset.
5. Returns Vitessce Widget information as a JSON response.

### Setup on a local machine
1. Create a folder to contain the **app.cfg** and local Anndata and Zarr files. There are three possible locations:
   * Bare metal: in a subdirectory named **spatial-query** of the user root (e.g., the resolution of "~" in MacOs) 
   * Docker: in the path _/usr/src/app_  of the volume mount
   * Environment variable **APP_CONFIG**
2. Copy the file **app.cfg.example** to a file named **app.cfg** in the folder. 
3. Edit the **app.cfg** file to provide the appropriate values of keys and secrets.
4. Access a dataset with spatially-resolved data products (e.g., HBM847.GZGD.668) in Data Portal.
5. Download the file **secondary_analysis.h5ad** from the Data Portal to the directory on the local machine.
6. View the JSON of the dataset in Data Portal.
7. Using the descendant UUIDs, find the location of the secondary_analysis.zarr path in Globus--e.g., _/a1d17fdd270a69c813b872a927dfa5f3/hubmap_ui/anndata-zarr/_.
8. Download the Zarr directory to the directory on the local machine.
9. Clone this repo.
10. Create a Python virtual environment.
11. Install the packages in **requirements.txt**.


# Service endpoints

#### Note on parameters
In the prototype application, all parameters are
passed to endpoints via session variables.

## /globus, /auth
These endpoints handle authentication to Globus. 
The endpoints work in tandem, and in fact redirect to each other in a loop until the user
is authenticated. Once the user has been authenticated, the /auth endpoint redirects to the /get_spqv route.

## /get_spqv
Performs Single Field of View (FOV) analysis of a dataset and provides results of analysis to the Vitessce plugin.

### Workflow
##### 1. Load spatial transcriptomics data for the UUID, using relative paths. 
It is necessary to:
1. Load the **secondary_analysis.h5ad** file associated with the dataset.
2. Identify the path to the **secondary_analysis.zarr** associated with the dataset.

The prototype application reads these files locally and manages them in the _Anndata_ class (**anndata.py**).

The production application will need either to point to files in Globus or download them locally.

##### 2. Initialize SpatialQuery Single FOV analysis
The prototype application encapsulates integration with SpatialQuery using the _SpatialQueryVitessce_ class (**spatialquery_vitessce.py**).

The **init** function of the __SpatialQueryVitessce_ class initializes SpatialQuery.

The **find_fp_knn** function of the class is an example of how to wrap calls to the SpatialQuery API.

##### 3. Initialize Vitessce SpatialQuery plugin
The _SpatialQueryVitessce_ class initializes the SpatialQuery Vitessce plugin.

##### 4. Configure Vitessce with dataset and views of interest. 
The **get_vitessce_widget** function of the _SpatialQueryVitessce_ class works with data from the _Anndata_ class 
to populate a Vitessce Widget with information from the SpatialQuery plugin.

##### 5. Render the Vitessce widget and pass the SpatialQueryPlugin instance.
The prototype application returns the Vitessce configuration as a JSON. 
The production application may need to return the native Vitessce object.

### response
* 200 -a JSON of Vitessce configuration information.
* Exception handling may include:
  * Passing along errors from SpatialQuery
  * 404 errors relating to invalid UUID or cell type
  * Passing along errors from Vitessce plugin


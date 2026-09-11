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
+ Via the UI, the user specifies parameters for SpatialQuery, including:
  + a cell type of interest (or “central cell type”) that the FOV analysis uses as an “anchor” for motif enrichment
  + relevant analysis parameters--e.g., the number of nearest neighbors (_k_). Consult the [SpatialQuery API](https://spatialquery.readthedocs.io/en/latest/api/single_data.html) documentation for descriptions of analysis parameters.

## Outputs
JSON results of SpatialQuery analysis.

---
# SpatialQuery Service integration
The SpatialQuery service will support integration with 
* the appropriate environment (HuBMAP or SenNet) API endpoints (i.e., in entity-api, uuid-api, ingest-api, etc.)
* SpatialQuery API endpoints
* ~calls to the SpatialQuery Vitessce Widget~

The service will reside in a component that is common to both the HuBMAP and SenNet environments.

# Service architecture
1. The SpatialQuery service will be a Flask application that manages calls to the various services and APIs.
2. The service will have direct access to the PSC file system in which secondary analysis files are stored.

# Service requirements
1. The service will use the environment-appropriate api to obtain the UUID of spatially resolved datasets.
2. The service will encapsulate calls to the SpatialQuery API and SpatialQuery Vitessce widget.

# PROTOTYPES

## 1. Jupyter notebook

A prototype using the SpatialQuery API is available as a Jupyter Notebook in a HuBMAP Workspace. 

To launch the workspace,
1. Log in to the HuBMAP Data Portal with a user with Workspace privileges.
2. Select the dataset with HuBMAP ID HBM847.GZGD.668.
3. In the far right menu of the dataset view, select Workspace.
4. Specify the Python kernel (at least 3.10) and the SpatialQuery template.

The notebook is related to [Tutorial 1](https://spatialquery.readthedocs.io/en/latest/tutorials/tutorial_1.html) in the SpatialQuery documentation site.

## 2. Python prototype application
The _app_ directory of this repository contains a Web application that performs Single FOV analysis on a dataset.

The application:
1. Displays a web page with a form that allows the user the specify 
    * consortium
    * dataset id
    * SpatialQuery analysis parameters
    * back end endpoint
2. Authenticates to the appropriate Globus consortium.
3. Loads H5AD and Zarr files for the dataset from a local store.
4. Performs Single FOV analysis on the specified dataset.
5. Returns JSON responses to endpoints.

### Setting up on a local machine
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
12. If PyCharm is the Python IDE, optionally set up a run configuration that runs the **app.py** script.
12. Start the application.
13. Open http://127.0.0.1:5000 to launch the prototype home page (index.html).
14. In the home page, select an endpoint from the "SpatialQuery service endpoint path" list.
15. Optionally edit values of parameters or accept defaults.
15. Click the "Call SpatialQuery endpoint" button.

# Service endpoints

#### Note on parameters
In the prototype application, all parameters are
passed from the home page to endpoints via session variables. This is 
required for Globus authentication. However, the endpoint routes assume that 
parameters are either in the path (the dataset id)
or in the request (i.e., are query parameters).

## /globus, /auth
These endpoints handle authentication to Globus for the prototype application. A production
version would likely use a standard authentication architecture.

The endpoints demonstrate how to authenticate to both HuBMAP and SenNet Globus environments via a
"consortium" parameter.

The endpoints work in tandem. They redirect to each other in a loop until the user
is authenticated. 
Once the user has been authenticated, the /auth endpoint redirects to the endpoint specified by the home page.

## relevant SpatialQuery endpoints

Reads secondary analysis files related to a spatially-resolved dataset and performs single FOV analysis.
### /find_fp_knn
### /find_fp_dist
### /motif_enrichment_knn
### /motif_enrichment_dist

### Workflow for all SpatialQuery endpoints
##### 1. Identify the dataset's descendant with files
In general, a specified dataset is part of a provenance chain of datasets. 
To identify the set of secondary analysis files to use for Vitessce, the application
examines the dataset and its descendant datasets and identifies the uuid for the 
latest published descendant dataset. 

The **datasetwithfiles.py** class file contains the code to identify files for a dataset.

##### 2. Load spatial transcriptomics data for the UUID, using relative paths. 
It is necessary to:
1. Load the **secondary_analysis.h5ad** file associated with the dataset.
2. Identify the path to the **secondary_analysis.zarr** associated with the dataset.

The prototype application reads these files from the proveanance file system (PSC) and manages them in the _SpatialQueryVitessce_ class (**spatialqueryvitessce_manager.py**).

##### 3. Initialize SpatialQuery Single FOV analysis
The prototype application encapsulates integration with SpatialQuery using the _SpatialQueryVitessce_ class (**spatialquery_vitessce.py**).

The **init** function of the __SpatialQueryVitessce_ class initializes SpatialQuery.

##### 4. Execute specified endpoint
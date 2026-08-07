# SpatialQuery Service
## Background
### Project Milestone
[Link](https://github.com/hubmapconsortium/pitt-milestones/issues/86)

### SpatialQuery documentation
[Link](https://spatialquery.readthedocs.io/en/latest/)

## Objectives

The HuBMAP Data Portal provides access to datasets containing spatially 
resolved transcriptomics data from modalities including 
Slide-seq, Visium, Xenium, CODEX, PhenoCycler, MIBI, and CellDIVE. 

These datasets can be analyzed by the SpatialQuery package to 
+ identify cell-type spatial co-occurrence patterns (motifs)
+ perform motif enrichment analysis
+ conduct motif-associated molecular analysis within spatial neighborhoods.

[SpatialQuery](https://github.com/ShaokunAn/Spatial-Query/blob/2d0f76e5390b81467758932efb1b6103fa220be1/README.md) is a class-based package that is initialized by loading the AnnData file (.h5ad) for a specified HuBMAP dataset. SpatialQuery offers parameterized analysis functions that return Pandas DataFrames of information related to the dataset.

## Use case
The prototype use case for SpatialQuery in the HuBMAP Data Portal is the Vitessce visualization of the Single Field Of View (FOV) analysis of a spatially resolved transcriptomics dataset. 

### Inputs
+ The end user selects a spatially resolved dataset from the Data Portal.
+ The end user specifies a cell type of interest (or “central cell type”) that the FOV analysis uses as an “anchor” for motif enrichment.

### Outputs
The Data Portal displays a separate Vitessce visualization of the SpatialQuery FOV results for the selected dataset and cell type.

## Prototype integration/Tutorial

A prototype using the SpatialQuery API is available as a Jupyter Notebook in a HuBMAP Workspace. 

To launch the workspace,
1. Log in to the HuBMAP Data Portal with a user with Workspace privileges.
2. Select the dataset with HuBMAP ID HBM847.GZGD.668.
3. In the far right menu of the dataset view, select Workspace.
4. Specify the SpatialQuery environment.

The notebook is the basis for [Tutorial 1](https://spatialquery.readthedocs.io/en/latest/tutorials/tutorial_1.html) in the SpatialQuery documentation site.

# Work in Progress
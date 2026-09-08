"""
spatialquery.py

Obtains inputs to be used to configure a SpatialQuery Vitessce configuration.

"""
from flask import Blueprint, make_response, jsonify, session, request,abort
import numpy as np
import scanpy as sc

from models.datasetwithfiles import DatasetWithFiles
from models.spatialquery_manager import SpatialQueryManager

spatialquery_blueprint = Blueprint('spatialquery', __name__, url_prefix='/spatialquery')

@spatialquery_blueprint.route('/vitessce-config/<datasetid>', methods=['GET'])
def get_spatialqueryvitessce_config(datasetid):

    """
    Obtain for the specified dataset id:
    1. uuid
    2. uuid for the dataset in the dataset's provenance chain that
       has secondary analysis files
    3. absolute file path to the secondary analysis files
    """
    print(f'Getting file information for dataset {datasetid}')
    dataset_with_files = DatasetWithFiles(dataset_id=datasetid)

    """
    Initialize SpatialQuery using the secondary analysis files.
    """
    spv = SpatialQueryManager(absolute_file_path=dataset_with_files.absolute_file_path)
    vcwidget = spv.get_vitessce_widget()

    dict_response = {
        "dataset_info":{
            "id": datasetid,
            "uuid": dataset_with_files.dataset_uuid
        },
        "file_info":{
            "file_dataset_uuid":dataset_with_files.file_uuid,
            #"files":dataset_with_files.files,
            "absolute_file_path":dataset_with_files.absolute_file_path
        },
        "config":vcwidget
    }

    return make_response(jsonify(dict_response), 200)

@spatialquery_blueprint.route('/find_fp_knn/<datasetid>', methods=['GET'])
def get_spatialquery_find_fp_knn(datasetid):

    """
        Obtain for the specified dataset id:
        1. uuid
        2. uuid for the dataset in the dataset's provenance chain that
           has secondary analysis files
        3. absolute file path to the secondary analysis files
        """
    print(f'Getting file information for dataset {datasetid}')
    dataset_with_files = DatasetWithFiles(dataset_id=datasetid)

    """
    Initialize SpatialQuery using the secondary analysis files.
    """
    spv = SpatialQueryManager(absolute_file_path=dataset_with_files.absolute_file_path)

    ct = request.args.get('ct')
    if ct is None:
        ct = "podocyte"

    k = request.args.get('k')
    if k is None:
        k = 30
    else:
        k = int(k)

    min_support = request.args.get('min_support')
    if min_support is None:
        min_support = 0.7
    else:
        min_support = float(min_support)

    max_dist = request.args.get('max_dist')
    if max_dist is None:
        max_dist = 20
    else:
        max_dist = float(max_dist)

    dict_response = spv.find_fp_knn(ct=ct, k=k, min_support=min_support, max_dist=max_dist)
    return make_response(jsonify(dict_response), 200)


@spatialquery_blueprint.route('/find_fp_dist/<datasetid>', methods=['GET'])
def get_spatialquery_find_fp_dist(datasetid):

    """
        Obtain for the specified dataset id:
        1. uuid
        2. uuid for the dataset in the dataset's provenance chain that
           has secondary analysis files
        3. absolute file path to the secondary analysis files
        """
    print(f'Getting file information for dataset {datasetid}')
    dataset_with_files = DatasetWithFiles(dataset_id=datasetid)

    """
    Initialize SpatialQuery using the secondary analysis files.
    """
    spv = SpatialQueryManager(absolute_file_path=dataset_with_files.absolute_file_path)

    ct = request.args.get('ct')
    if ct is None:
        ct = "podocyte"


    min_support = request.args.get('min_support')
    if min_support is None:
        min_support = 0.7
    else:
        min_support = float(min_support)

    max_dist = request.args.get('max_dist')
    if max_dist is None:
        max_dist = 20
    else:
        max_dist = float(max_dist)

    min_size = request.args.get('max_size')
    if min_size is None:
        min_size = 0
    else:
        min_size = float(min_size)

    dict_response = spv.find_fp_dist(ct=ct, max_dist=max_dist, min_size=min_size, min_support=min_support)
    return make_response(jsonify(dict_response), 200)

@spatialquery_blueprint.route('/find_patterns_grid/<datasetid>', methods=['GET'])
def get_spatialquery_patterns_grid(datasetid):

    """
        Obtain for the specified dataset id:
        1. uuid
        2. uuid for the dataset in the dataset's provenance chain that
           has secondary analysis files
        3. absolute file path to the secondary analysis files
        """
    print(f'Getting file information for dataset {datasetid}')
    dataset_with_files = DatasetWithFiles(dataset_id=datasetid)

    """
    Initialize SpatialQuery using the secondary analysis files.
    """
    spv = SpatialQueryManager(absolute_file_path=dataset_with_files.absolute_file_path)


    min_support = request.args.get('min_support')
    if min_support is None:
        min_support = 0.7
    else:
        min_support = float(min_support)

    max_dist = request.args.get('max_dist')
    if max_dist is None:
        max_dist = 20
    else:
        max_dist = float(max_dist)

    min_size = request.args.get('max_size')
    if min_size is None:
        min_size = 0
    else:
        min_size = float(min_size)

    if_display = request.args.get('if_display')
    if if_display is None:
        if_display = True
    else:
        if_display = if_display.upper()=="TRUE"

    figsize_width = request.args.get('figsize_width')
    if figsize_width is None:
        figsize_width=10
    else:
        figsize_width = int(figsize_width)
    figsize_height = request.args.get('figsize_height')
    if figsize_height is None:
        figsize_height = 5
    else:
        figsize_height = int(figsize_height)

    return_cellID = request.args.get('return_cellID')
    if return_cellID is None:
        return_cellID = False
    else:
        return_cellID = return_cellID.upper() == "TRUE"

    return_grid=request.args.get('return_grid')
    if return_grid is None:
        return_grid = False
    else:
        return_grid = return_grid.upper() == "TRUE"

    dict_response = spv.find_patterns_grid(max_dist=max_dist,
                                           min_size=min_size,
                                           min_support=min_support,
                                           if_display=if_display,
                                           figsize=(figsize_width, figsize_height),
                                           return_cellID=return_cellID,
                                           return_grid=return_grid)
    return make_response(jsonify(dict_response), 200)

@spatialquery_blueprint.route('/find_patterns_rand/<datasetid>', methods=['GET'])
def get_spatialquery_patterns_rand(datasetid):

    """
        Obtain for the specified dataset id:
        1. uuid
        2. uuid for the dataset in the dataset's provenance chain that
           has secondary analysis files
        3. absolute file path to the secondary analysis files
        """
    print(f'Getting file information for dataset {datasetid}')
    dataset_with_files = DatasetWithFiles(dataset_id=datasetid)

    """
    Initialize SpatialQuery using the secondary analysis files.
    """
    spv = SpatialQueryManager(absolute_file_path=dataset_with_files.absolute_file_path)


    min_support = request.args.get('min_support')
    if min_support is None:
        min_support = 0.7
    else:
        min_support = float(min_support)

    max_dist = request.args.get('max_dist')
    if max_dist is None:
        max_dist = 20
    else:
        max_dist = float(max_dist)

    n_points = request.args.get('n_points')
    if n_points is None:
        n_points = 1000
    else:
        n_points = int(n_points)

    min_size = request.args.get('max_size')
    if min_size is None:
        min_size = 0
    else:
        min_size = float(min_size)

    if_display = request.args.get('if_display')
    if if_display is None:
        if_display = True
    else:
        if_display = if_display.upper()=="TRUE"

    figsize_width = request.args.get('figsize_width')
    if figsize_width is None:
        figsize_width=10
    else:
        figsize_width = int(figsize_width)
    figsize_height = request.args.get('figsize_height')
    if figsize_height is None:
        figsize_height = 5
    else:
        figsize_height = int(figsize_height)

    return_cellID = request.args.get('return_cellID')
    if return_cellID is None:
        return_cellID = False
    else:
        return_cellID = return_cellID.upper() == "TRUE"

    return_grid=request.args.get('return_grid')
    if return_grid is None:
        return_grid = False
    else:
        return_grid = return_grid.upper() == "TRUE"

    seed = request.args.get('seed')
    if seed is None:
        seed = 2023
    else:
        seed = int(seed)

    dict_response = spv.find_patterns_rand(max_dist=max_dist,
                                           n_points=n_points,
                                           min_support=min_support,
                                           min_size=min_size,
                                           if_display=if_display,
                                           figsize=(figsize_width, figsize_height),
                                           return_cellID=return_cellID,
                                           seed=seed)
    return make_response(jsonify(dict_response), 200)

@spatialquery_blueprint.route('/motif_enrichment_knn/<datasetid>', methods=['GET'])
def get_spatialquerymotif_enrichment_knn(datasetid):

    """
        Obtain for the specified dataset id:
        1. uuid
        2. uuid for the dataset in the dataset's provenance chain that
           has secondary analysis files
        3. absolute file path to the secondary analysis files
        """
    print(f'Getting file information for dataset {datasetid}')
    dataset_with_files = DatasetWithFiles(dataset_id=datasetid)

    """
    Initialize SpatialQuery using the secondary analysis files.
    """
    spv = SpatialQueryManager(absolute_file_path=dataset_with_files.absolute_file_path)

    ct = request.args.get('ct')
    if ct is None:
        ct = "podocyte"

    k = request.args.get('k')
    if k is None:
        k = 30
    else:
        k = int(k)

    motifs = request.args.get('motifs')
    if motifs == "None":
        motifs = [ct]
    else:
        motifs = motifs.split(',')

    min_support = request.args.get('min_support')
    if min_support is None:
        min_support = 0.7
    else:
        min_support = float(min_support)

    max_dist = request.args.get('max_dist')
    if max_dist is None:
        max_dist = 20
    else:
        max_dist = float(max_dist)

    return_cellID = request.args.get('return_cellID')
    if return_cellID is None:
        return_cellID = False
    else:
        return_cellID = return_cellID.upper() == "TRUE"

    dict_response = spv.motif_enrichment_knn(ct=ct, k=k, motifs=motifs, min_support=min_support, max_dist=max_dist, return_cellID=return_cellID)
    return make_response(jsonify(dict_response), 200)

@spatialquery_blueprint.route('/motif_enrichment_dist/<datasetid>', methods=['GET'])
def get_spatialquerymotif_enrichment_dist(datasetid):

    """
        Obtain for the specified dataset id:
        1. uuid
        2. uuid for the dataset in the dataset's provenance chain that
           has secondary analysis files
        3. absolute file path to the secondary analysis files
        """
    print(f'Getting file information for dataset {datasetid}')
    dataset_with_files = DatasetWithFiles(dataset_id=datasetid)

    """
    Initialize SpatialQuery using the secondary analysis files.
    """
    spv = SpatialQueryManager(absolute_file_path=dataset_with_files.absolute_file_path)

    ct = request.args.get('ct')
    if ct is None:
        ct = "podocyte"


    motifs = request.args.get('motifs')
    if motifs == "None":
        motifs = [ct]
    else:
        motifs = motifs.split(',')

    min_support = request.args.get('min_support')
    if min_support is None:
        min_support = 0.7
    else:
        min_support = float(min_support)

    max_dist = request.args.get('max_dist')
    if max_dist is None:
        max_dist = 20
    else:
        max_dist = float(max_dist)

    min_size = request.args.get('min_size')
    if min_size is None:
        min_size = 0
    else:
        min_size = float(min_size)

    return_cellID = request.args.get('return_cellID')
    if return_cellID is None:
        return_cellID = False
    else:
        return_cellID = return_cellID.upper() == "TRUE"

    dict_response = spv.motif_enrichment_dist(ct=ct, motifs=motifs, max_dist=max_dist, min_size=min_size, min_support=min_support,return_cellID=return_cellID)
    return make_response(jsonify(dict_response), 200)

@spatialquery_blueprint.route('/de_genes/<datasetid>', methods=['GET'])
def get_spatialquery_de_genes(datasetid):

    """
        Obtain for the specified dataset id:
        1. uuid
        2. uuid for the dataset in the dataset's provenance chain that
           has secondary analysis files
        3. absolute file path to the secondary analysis files
        """

    print(f'Getting file information for dataset {datasetid}')
    dataset_with_files = DatasetWithFiles(dataset_id=datasetid)

    """
    Initialize SpatialQuery using the secondary analysis files.
    """
    print('initializing SpatialQuery object')
    spv = SpatialQueryManager(absolute_file_path=dataset_with_files.absolute_file_path)

    """
    The SpatialQueryManager object's wrapper functions (e.g., find_kp_knn)
    call corresponding functions of the SpatialQuery object.
    The SpatialQuery object returns dataframes; the SpatialQueryManager object
    converts these dataframes into dicts for reponsse.
    For the multu-step analysis that follows, use the dataframes of the SpatialQuery
    object.
    """

    ct = request.args.get('ct')
    if ct is None:
        ct = "podocyte"

    """
    Identify frequent patterns.
    """

    print(f'Calling find_fp_knn for {ct}')
    fp_knn = spv.single_sp.find_fp_knn(
        ct=ct,
        k=30,
        min_support=0.5#,
       # max_dist=20
    )

    """
    Specify a motif from the frequent pattern results
    """

    # Specify a motif from the frequent pattern results.
    motif = list(fp_knn['itemsets'][0])
    motif_sig_custom = spv.single_sp.motif_enrichment_knn(
        ct=ct,
        motifs=motif,
        k=30,
    )

    # Enrich on the specified motif.
    motif = motif_sig_custom['motifs'][0]
    motif_result_dist = spv.single_sp.motif_enrichment_dist(
        ct=ct,
        motifs=motif,
        max_dist=10,
        return_cellID=True
    )

    center_id = motif_result_dist["center_id"].iloc[0]
    all_center_id = np.where(spv.single_sp.labels == ct)[0]
    non_center_id = np.setdiff1d(all_center_id, center_id)

    print(f"Motif+ anchor cells: {len(center_id)}")
    print(f"Motif− anchor cells: {len(non_center_id)}")

    print('Calling de_genes')
    de_result = spv.single_sp.de_genes(
        ind_group1=center_id,
        ind_group2=non_center_id,
        min_fraction=0.05,
        method="t-test",
        alpha=0.05,
    )

    print(f"Number of DE genes: {len(de_result)}")
    dict_response = de_result.to_dict()

    return make_response(jsonify(dict_response), 200)

@spatialquery_blueprint.route('/compute_gene_gene_correlation/<datasetid>', methods=['GET'])
def get_spatialquery_compute_gene_gene_correlation(datasetid):

    """
        Obtain for the specified dataset id:
        1. uuid
        2. uuid for the dataset in the dataset's provenance chain that
           has secondary analysis files
        3. absolute file path to the secondary analysis files
        """

    print(f'Getting file information for dataset {datasetid}')
    dataset_with_files = DatasetWithFiles(dataset_id=datasetid)

    """
    Initialize SpatialQuery using the secondary analysis files.
    """
    print('Initializing SpatialQuery object')
    spv = SpatialQueryManager(absolute_file_path=dataset_with_files.absolute_file_path)

    """
        The SpatialQueryManager object's wrapper functions (e.g., find_kp_knn)
        call corresponding functions of the SpatialQuery object.
        The SpatialQuery object returns dataframes; the SpatialQueryManager object
        converts these dataframes into dicts for reponsse.
        For the multu-step analysis that follows, use the dataframes of the SpatialQuery
        object.
    """

    print('Obtaining highly-variable gene list')
    adata_tmp = spv.single_sp.adata.copy()
    sc.pp.highly_variable_genes(adata_tmp, n_top_genes=3000)
    hvg = adata_tmp.var[adata_tmp.var['highly_variable']].index.tolist()

    ct = request.args.get('ct')
    if ct is None:
        ct = "podocyte"

    """
    Identify frequent patterns.
    """
    print(f'Calling find_fp_knn for {ct}')
    fp_knn = spv.single_sp.find_fp_knn(
        ct=ct,
        k=30,
        min_support=0.5  # ,
        # max_dist=20
    )

    motif = list(fp_knn['itemsets'][0])
    print('Calling compute_gene_gene_correlation_by_type')
    gene_pair_df = spv.single_sp.compute_gene_gene_correlation_by_type(
        ct=ct,
        motif=motif,
        genes=hvg,  # specify genes to compute gene-gene correlation, or use all genes by setting genes=None
        max_dist=10,  # define neighborhood size with radius-based neighborhood, or specify k for knn-based neighborhood
    )

    gene_pair_df = gene_pair_df[gene_pair_df['if_significant']]

    dict_response = gene_pair_df.to_dict()

    return make_response(jsonify(dict_response), 200)
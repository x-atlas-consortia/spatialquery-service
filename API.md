# SpatialQuery Service API

Returns cell neighborhood analyses for spatially resolved HuBMAP datasets. All endpoints are GET and return JSON.

Base URL: `https://spatial.api.hubmapconsortium.org`

## Authentication

Send a Globus Groups token in the `Authorization` header:

    Authorization: Bearer <token>

The user must be a member of HuBMAP-Read.

## Notes

- `datasetid` is a HuBMAP ID or UUID. If the dataset has no analysis files of its own, the service uses its most recent published descendant that has a spatial assay type and contains `secondary_analysis.h5ad`.
- The analysis file is loaded on every request, so response times range from several seconds to a few minutes.
- `ct` must match a cell type label in the dataset exactly. The default is `podocyte`.
- `max_dist` is in normalized units, where the mean nearest neighbor distance is 1.
- Cell IDs are zero-based row positions in `secondary_analysis.h5ad`.
- Parameters and result fields are defined in the [SpatialQuery documentation](https://spatialquery.readthedocs.io/).

## GET /spatialquery/find_fp_knn/{datasetid}

Returns the combinations of cell types that most often occur among the nearest neighbors of cells of type `ct`.

| Parameter | In | Type | Required | Default |
|---|---|---|---|---|
| datasetid | path | string | Yes | None |
| ct | query | string | No | podocyte |
| k | query | integer | No | 30 |
| min_support | query | number | No | 0.7 |
| max_dist | query | number | No | 20 |

Example:

    curl -H "Authorization: Bearer <token>" \
      "https://spatial.api.hubmapconsortium.org/spatialquery/find_fp_knn/HBM847.GZGD.668?ct=podocyte"

Response: a list of objects.

| Field | Type | Description |
|---|---|---|
| itemsets | list of strings | Cell types in the combination |
| support | number | Frequency of the combination |

    [
      {
        "itemsets": [
          "glomerular capillary endothelial cell",
          "kidney loop of Henle cortical thick ascending limb epithelial cell",
          "podocyte"
        ],
        "support": 0.8671875
      },
      {
        "itemsets": [
          "kidney loop of Henle cortical thick ascending limb epithelial cell",
          "peritubular capillary endothelial cell"
        ],
        "support": 0.703125
      }
    ]

## GET /spatialquery/find_fp_dist/{datasetid}

Returns the combinations of cell types that most often occur within a set distance of cells of type `ct`.

| Parameter | In | Type | Required | Default |
|---|---|---|---|---|
| datasetid | path | string | Yes | None |
| ct | query | string | No | podocyte |
| min_support | query | number | No | 0.7 |
| max_dist | query | number | No | 20 |
| min_size | query | number | No | 0 |

Response: same as `/spatialquery/find_fp_knn`.

## GET /spatialquery/motif_enrichment_knn/{datasetid}

Tests whether a combination of cell types occurs among the nearest neighbors of cells of type `ct` more often than expected by chance.

| Parameter | In | Type | Required | Default | Description |
|---|---|---|---|---|---|
| datasetid | path | string | Yes | None | |
| ct | query | string | No | podocyte | |
| motifs | query | string | No | value of ct | Comma-separated cell types forming one combination |
| k | query | integer | No | 30 | |
| max_dist | query | number | No | 20 | |
| return_cellID | query | boolean | No | false | Include cell IDs in the response |

Response: a list of objects, one per combination tested.

| Field | Type | Description |
|---|---|---|
| center | string | Cell type given in `ct` |
| motifs | list of strings | Cell types in the combination, sorted |
| n_center_motif | integer | Cells of type `ct` with the combination in their neighborhood |
| n_center | integer | Total cells of type `ct` |
| n_motif | integer | Cells of any type with the combination in their neighborhood |
| expectation | number | Expected count by chance |
| p-values | number | p-value of the test |
| if_significant | boolean | True if p < 0.05 |
| adj-pval | number | Corrected p-value. Present when multiple combinations are tested |
| center_id | list of integers | Present when return_cellID is true |
| neighbor_id | list of integers | Present when return_cellID is true |

## GET /spatialquery/motif_enrichment_dist/{datasetid}

Tests whether a combination of cell types occurs within a set distance of cells of type `ct` more often than expected by chance.

| Parameter | In | Type | Required | Default | Description |
|---|---|---|---|---|---|
| datasetid | path | string | Yes | None | |
| ct | query | string | No | podocyte | |
| motifs | query | string | No | value of ct | Comma-separated cell types forming one combination |
| max_dist | query | number | No | 20 | |
| return_cellID | query | boolean | No | false | Include cell IDs in the response |

Response: same as `/spatialquery/motif_enrichment_knn`.

## Errors

Errors from the service are JSON: `{"error": "message"}`. The 401 and 403 responses are plain text.

| Status | Cause |
|---|---|
| 400 | Non-numeric parameter, ID is not a dataset, or the analysis file lacks spatial coordinates, gene names or cell type labels |
| 401 | Missing or invalid token |
| 403 | User is not in HuBMAP-Read |
| 404 | Dataset not found, no qualifying analysis file, or file missing on disk |
| 500 | Unhandled error, including a `ct` not present in the dataset |
| 502 | entity-api or ingest-api returned an error |
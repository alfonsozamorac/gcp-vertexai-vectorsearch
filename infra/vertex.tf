
provider "google" {
  region  = var.region
  project = var.project_id
}

data "google_project" "project" {
  project_id = var.project_id
}

resource "google_storage_bucket" "bucket" {
  name                        = "vertex-index-confluence"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
}

resource "google_vertex_ai_index" "index" {
  region       = var.region
  display_name = "confluence-index"
  description  = "index for confluence article"
  labels       = var.labels
  metadata {
    contents_delta_uri = "gs://${google_storage_bucket.bucket.name}"
    config {
      dimensions                  = 768
      approximate_neighbors_count = 100
      shard_size                  = "SHARD_SIZE_SMALL"
      distance_measure_type       = "DOT_PRODUCT_DISTANCE"
      algorithm_config {
        tree_ah_config {
          leaf_node_embedding_count    = 500
          leaf_nodes_to_search_percent = 7
        }
      }
    }
  }
  index_update_method = "STREAM_UPDATE"
}

resource "google_vertex_ai_index_endpoint" "index_endpoint" {
  display_name = "confluence-index-endpoint"
  description  = "Confluence vertex endpoint"
  region       = var.region
  labels       = var.labels
  network      = "projects/${data.google_project.project.number}/global/networks/${google_compute_network.vertex_network.name}"
  depends_on = [
    google_service_networking_connection.private_vpc_connection
  ]
}

resource "google_vertex_ai_index_endpoint_deployed_index" "deployed_index" {
  index_endpoint        = google_vertex_ai_index_endpoint.index_endpoint.id
  index                 = google_vertex_ai_index.index.id
  deployed_index_id     = "confluence_index_deployed"
  enable_access_logging = false
  display_name          = "confluence_index_deployed"

  dedicated_resources {
    machine_spec {
      machine_type = "e2-standard-16"
    }
    min_replica_count = 1
    max_replica_count = 3
  }
}

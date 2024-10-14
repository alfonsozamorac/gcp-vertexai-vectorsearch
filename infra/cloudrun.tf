
# Create an Artifact Registry repository
resource "google_artifact_registry_repository" "docker_repo" {
  repository_id = "repository-vertex-cloudrun"
  format        = "DOCKER"
  location      = var.region
}

resource "google_secret_manager_secret" "secret" {
  secret_id = "confluence-secret-auth"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "secret-version" {
  secret      = google_secret_manager_secret.secret.id
  secret_data = file("./.env")
}

# Create a Cloud Run Service
resource "google_cloud_run_v2_service" "vertexai_service" {
  count = var.create_cloudrun == true ? 1 : 0

  name                = "cloudrun-job-vertex"
  location            = var.region
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"
  template {
    volumes {
      name = "confluence-volume"
      secret {
        secret       = google_secret_manager_secret.secret.secret_id
        default_mode = 256
        items {
          version = "latest"
          path    = google_secret_manager_secret.secret.secret_id
          mode    = 256
        }
      }
    }
    containers {
      image = "${google_artifact_registry_repository.docker_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.name}/cloudrun-vertex:latest"
      volume_mounts {
        name       = "confluence-volume"
        mount_path = "/secrets"
      }
      ports {
        container_port = 8080
      }
    }
    vpc_access {
      connector = google_vpc_access_connector.vpc_connector.id
      egress    = "ALL_TRAFFIC"
    }
  }

  depends_on = [
    google_secret_manager_secret_version.secret-version
  ]
}

output "index_id" {
  description = "Index ID"
  value       = google_vertex_ai_index.index.id
}

output "index_endpoint_id" {
  description = "Index Endpoint ID"
  value       = google_vertex_ai_index_endpoint.index_endpoint.id
}

output "deployed_index_id" {
  description = "Deployed Index ID"
  value       = google_vertex_ai_index_endpoint_deployed_index.deployed_index.id
}

output "network_selflink" {
  description = "Network selflink"
  value       = google_compute_network.vertex_network.self_link
}

output "ip_address" {
  description = "IP Adress"
  value       = google_compute_global_address.private_ip_address.address
}

output "cloudrun_uri" {
  description = "Cloud Run URI"
  value       = try(google_cloud_run_v2_service.vertexai_service.0.uri, null)
}

output "repository_id" {
  description = "Artifact registry repository"
  value       = google_artifact_registry_repository.docker_repo.repository_id
}
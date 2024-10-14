resource "google_compute_network" "vertex_network" {
  project                 = var.project_id
  name                    = "confluence-rag-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "subnetwork"
  region        = var.region
  network       = google_compute_network.vertex_network.id
  ip_cidr_range = "10.0.0.0/28"
}

resource "google_compute_global_address" "private_ip_address" {
  name          = "private-ip-address"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vertex_network.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vertex_network.name
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

resource "google_vpc_access_connector" "vpc_connector" {
  name          = "cloudrun-vpc-connector"
  region        = var.region
  min_instances = 2
  max_instances = 3
  subnet {
    name = google_compute_subnetwork.subnet.name
  }
}

#NAT
resource "google_compute_router" "router" {
  name    = "vertex-router"
  network = google_compute_network.vertex_network.id
  region  = var.region
  bgp {
    asn = 64514
  }
}

resource "google_compute_router_nat" "nat" {
  name                               = "router-nat"
  router                             = google_compute_router.router.name
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  min_ports_per_vm                   = 64
  subnetwork {
    name                    = google_compute_subnetwork.subnet.id
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

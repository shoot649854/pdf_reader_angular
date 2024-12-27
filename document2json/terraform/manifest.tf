resource "google_cloudfunctions_function" "process_pdf" {
  name        = "process-pdf"
  build_config {
    runtime     = "custom"
    entry_point = "process_pdf"
    image = "us-central1-docker.pkg.dev/my-project-123/my-repo/my-func-image:latest"
  }
  service_config {
    max_instance_count = 3
    available_memory   = "512M"
  }
  event_trigger {
    event_type     = "google.cloud.storage.object.v1.finalized"
    resource       = "projects/_/buckets/<YOUR_BUCKET_NAME>"
    trigger_region = "us-central1"
  }
}

terraform {
  backend "gcs" {
    bucket  = "yoppy-chatbot-terraform-backet"
  }
}

provider "google" {
  project     = "yoppy-chatbot"
  region = "asia-northeast1"
}

resource "google_pubsub_topic" "chatcall" {
  name = "pubsub-chatcall"
}

resource "google_pubsub_topic" "countup" {
  name = "pubsub-countup"
}

resource "google_cloud_scheduler_job" "countup" {
  name        = "scheduler-countup"
  description = "毎日0時に今日のカウントを1増やす"
  schedule    = "0 0 * * *"
  time_zone   = "Asia/Tokyo"

  pubsub_target {
    # topic.id is the topic's full resource name.
    topic_name = google_pubsub_topic.countup.id
    data       = base64encode("countup")
  }

  retry_config {
    max_backoff_duration = "3600s"
    max_doublings = 5
    max_retry_duration = "0s"
    min_backoff_duration = "5s"
    retry_count = 0
  }

  timeouts {}
}

resource "google_cloud_scheduler_job" "callchat-1" {
  name        = "scheduler-callchat-1"
  description = "毎日6時半に今日洗うものを通知する"
  schedule    = "30 6 * * *"
  time_zone   = "Asia/Tokyo"

  pubsub_target {
    # topic.id is the topic's full resource name.
    topic_name = google_pubsub_topic.chatcall.id
    data       = base64encode("call at 6:30")
  }

  retry_config {
    max_backoff_duration = "3600s"
    max_doublings = 5
    max_retry_duration = "0s"
    min_backoff_duration = "5s"
    retry_count = 0
  }

  timeouts {}
}

resource "google_cloud_scheduler_job" "callchat-2" {
  name        = "scheduler-callchat-2"
  description = "毎日12時に今日洗うものを通知する"
  schedule    = "0 12 * * *"
  time_zone   = "Asia/Tokyo"

  pubsub_target {
    # topic.id is the topic's full resource name.
    topic_name = google_pubsub_topic.chatcall.id
    data       = base64encode("call at 12:00")
  }

  retry_config {
    max_backoff_duration = "3600s"
    max_doublings = 5
    max_retry_duration = "0s"
    min_backoff_duration = "5s"
    retry_count = 0
  }

  timeouts {}
}

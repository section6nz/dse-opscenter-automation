import logging

import common
from config import OpsCenterConfiguration


def run_cluster_install(config: OpsCenterConfiguration, session_id, cluster_id):
  install_job = common.do_post(
      config,
      session_id,
      "actions/install",
      {"job-type": "install",
       "job-scope": "cluster",
       "resource-id": cluster_id,
       "concurrency-strategy": "cluster-at-a-time",
       "continue-on-error": "false"}
  )
  job_id = install_job['id']
  logging.info("Created install job_id=%s", job_id)
  return job_id

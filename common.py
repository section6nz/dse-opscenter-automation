import json
import logging
import os
import time

import requests

from config import OpsCenterConfiguration


def get_session_token(config: OpsCenterConfiguration):
  opscenter_session = os.environ.get('opscenter_session', None)

  if opscenter_session:
    return opscenter_session

  endpoint = "http://%s:8888/login" % config.server_ip

  post_data = {"username": config.username, "password": config.password}

  result = requests.post(endpoint, data=json.dumps(post_data))
  result_data = json.loads(result.text)

  session_id = result_data['sessionid']
  logging.info("Session ID: %s", session_id)
  return session_id


def do_get(config: OpsCenterConfiguration, session_id, url):
  base_url = 'http://%s:8888/api/v2/lcm/' % config.server_ip
  result = requests.get(base_url + url,
                        headers={'Content-Type': 'application/json', 'opscenter-session': session_id})
  if result.status_code >= 400:
    logging.error("OpsCenter API request failed: url=%s, status=%d, response=%s", result.url, result.status_code,
                  result.text)
    exit(1)
  logging.debug("%s", result.text)
  result_data = json.loads(result.text)
  return result_data


def do_post(config: OpsCenterConfiguration, session_id, url, post_data):
  base_url = 'http://%s:8888/api/v2/lcm/' % config.server_ip
  result = requests.post(base_url + url,
                         data=json.dumps(post_data),
                         headers={'Content-Type': 'application/json', 'opscenter-session': session_id})
  if result.status_code >= 400:
    logging.error("OpsCenter API request failed: url=%s, status=%d, response=%s", result.url, result.status_code,
                  result.text)
    exit(1)
  logging.debug("%s", result.text)
  result_data = json.loads(result.text)
  return result_data


def update_nodesync(config: OpsCenterConfiguration, session_id, url, cluster_name, post_data):
  base_url = 'http://%s:8888/' % config.server_ip
  result = requests.post(base_url + cluster_name + url,
                         data=json.dumps(post_data),
                         headers={'Content-Type': 'application/json', 'opscenter-session': session_id})
  if result.status_code >= 400:
    logging.error("OpsCenter API request failed: url=%s, status=%d, response=%s", result.url, result.status_code,
                  result.text)
    exit(1)
  logging.debug("%s", result.text)
  result_data = json.loads(result.text)
  return result_data


def wait_for_job(session_id, config: OpsCenterConfiguration, job_id):
  job_url = "jobs/%s" % job_id
  base_url = 'http://%s:8888/api/v2/lcm/' % config.server_ip
  job_log_url = base_url + 'opscenter/lcm.html#/jobs/%s' % job_id

  i = 0
  logging.info("Job is running... id=%s", job_id)
  while i < 50:
    job_response = requests.get(
        base_url + job_url,
        headers={'Content-Type': 'application/json', 'opscenter-session': session_id})
    logging.debug(job_response.text)

    # If the response is 404, the job may be pending, so we need to wait.
    if job_response.status_code == 404:
      logging.warning("Job may be pending, waiting a little... url=%s, status=%d, response=%s",
                    job_response.url, job_response.status_code, job_response.text)
      time.sleep(15)
      continue
    elif job_response.status_code >= 400:
      logging.error("OpsCenter API request failed: url=%s, status=%d, response=%s",
                    job_response.url, job_response.status_code, job_response.text)
      exit(1)

    job_results = json.loads(job_response.text)
    job_status = job_results.get('status')
    if job_status == 'COMPLETE':
      logging.info("The job has completed! id=%s, url=%s", job_id, job_log_url)
      break
    elif job_status == 'FAILED':
      logging.error("The job has failed! id=%s, url=%s", job_id, job_log_url)
      exit(1)
    elif job_status == 'WILL_FAIL':
      logging.error("The job will fail! id=%s, url=%s", job_id, job_log_url)
      exit(1)
    else:
      time.sleep(30)
    i += 1

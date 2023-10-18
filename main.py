import argparse
import logging

import common
from config import OpsCenterConfiguration
from tasks.cluster import create_cluster
from tasks.config_profile import create_config_profile
from tasks.credential import create_credential
from tasks.datacenter import create_datacenter
from tasks.node import create_nodes
from tasks.repo import create_repo
from tasks.install_cluster import run_cluster_install
from tasks.node_sync import enable_node_sync

parser = argparse.ArgumentParser(
    prog='DSE OpsCenter Configuration',
    description='Set up OpsCenter LCM with configuration')

parser.add_argument("--debug", help="Enable debug logging.", action='store_true')
parser.add_argument("--install", help="Run install job.", action='store_true', default=False)
parser.add_argument('-f', '--config', help='Location of config yaml. (default config/config.yaml)')
args = parser.parse_args()

config = OpsCenterConfiguration()
config.load_config(args.config)

if args.debug:
  logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
else:
  logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

logging.info("Logging in to Opscenter as user=%s", config.username)
session_id = common.get_session_token(config)

logging.info("Creating repository=%s", config.repository_name)
repo_id = create_repo(session_id, config)
logging.info("Creating credential=%s", config.install_credential_name)
credential_id = create_credential(session_id, config)
for config_profile in config.config_profiles:
  logging.info("Creating config_profile=%s", config_profile.name)
  create_config_profile(session_id, config, config_profile)

logging.info("Creating cluster=%s", config.cluster_name)
cluster_id = create_cluster(session_id, config, repo_id, credential_id, config.config_profile_name)

for datacenter_config in config.datacenter_configuration:
  logging.info("Creating datacenter=%s", datacenter_config.name)
  datacenter_id = create_datacenter(session_id, cluster_id, config, datacenter_config)
  for node_config in datacenter_config.node_configuration:
    logging.info("Adding node to datacenter=%s, node=%s", datacenter_config.name, node_config.name)
    node_id = create_nodes(session_id, config, datacenter_config, datacenter_id, node_config)

# Run install job if specified
if args.install:
  logging.info("Running install job.")
  job_id = run_cluster_install(config, session_id, cluster_id)
  common.wait_for_job(session_id, config, job_id)
  enable_node_sync(session_id, config)

from typing import List

from pyconfigparser import configparser, ConfigError
from schema import Use, And, Optional

SCHEMA_CONFIG = {
  'opscenter': {
    'opscenter_username': And(Use(str), lambda string: len(string) > 0),
    'opscenter_password': And(Use(str), lambda string: len(string) > 0),
    'opscenter_server_ip': And(Use(str), lambda string: len(string) > 0),
  },
  'dse': {
    'cluster_name': And(Use(str), lambda string: len(string) > 0),
    'datastax_version': And(Use(str), lambda string: len(string) > 0),
    'repository_name': And(Use(str), lambda string: len(string) > 0),
    'install_credential_name': And(Use(str), lambda string: len(string) > 0),
    'install_credential_username': And(Use(str), lambda string: len(string) > 0),
    'install_credential_key_file': And(Use(str), lambda string: len(string) > 0),
    'cassandra_default_password': And(Use(str), lambda string: len(string) > 0),
    Optional('node_sync'): [{
      'pattern': And(Use(str), lambda string: len(string) > 0),
    }]
  },
  'config_profiles': [{
    'name': And(Use(str), lambda string: len(string) > 0),
    Optional('cassandra_yaml'): Use(str),
    Optional('cassandra_env_sh'): Use(str),
    Optional('dse_env_sh'): Use(str),
  }],
  'cluster': {
    'config_profile_name': And(Use(str), lambda string: len(string) > 0),
    'datacenters': [{
      'name': And(Use(str), lambda string: len(string) > 0),
      'solr_enabled': And(Use(bool)),
      'spark_enabled': And(Use(bool)),
      'graph_enabled': And(Use(bool)),
      'hadoop_enabled': And(Use(bool)),
      Optional('config_profile_name'): Use(str),
      'nodes': [{
        'name': And(Use(str), lambda string: len(string) > 0),
        'private_ip': And(Use(str), lambda string: len(string) > 0),
        'node_ip': And(Use(str), lambda string: len(string) > 0),
        'rack': And(Use(str), lambda string: len(string) > 0),
        Optional('config_profile_name'): Optional(str),
      }]
    }]
  }
}


class NodeConfiguration:
  name = None
  private_ip = None
  node_ip = None
  rack = None
  config_profile_name = None

  def __init__(self, name, private_ip, node_ip, rack, config_profile_name=None):
    self.name = name
    self.private_ip = private_ip
    self.node_ip = node_ip
    self.rack = rack
    self.config_profile_name = config_profile_name


class DatacenterConfiguration:
  name = None
  solr_enabled = None
  spark_enabled = None
  graph_enabled = None
  hadoop_enabled = None
  config_profile_name = None

  node_configuration: List[NodeConfiguration] = None

  def __init__(self, name, solr_enabled, spark_enabled, graph_enabled, hadoop_enabled, node_configuration,
      config_profile_name=None):
    self.name = name
    self.solr_enabled = solr_enabled
    self.spark_enabled = spark_enabled
    self.graph_enabled = graph_enabled
    self.hadoop_enabled = hadoop_enabled
    self.node_configuration = node_configuration
    self.config_profile_name = config_profile_name


class ConfigProfileConfiguration:
  name = None
  cassandra_yaml = None
  cassandra_env_sh = None
  dse_env_sh = None

  def __init__(self, name, cassandra_yaml=None, cassandra_env_sh=None, dse_env_sh=None):
    self.name = name
    self.cassandra_yaml = cassandra_yaml
    self.cassandra_env_sh = cassandra_yaml
    self.dse_env_sh = cassandra_yaml


class NodeSyncConfiguration:
  pattern = None

  def __init__(self, pattern):
    self.pattern = pattern


class OpsCenterConfiguration:
  log_level = None
  cluster_name = None
  datastax_version = None
  repository_name = None
  config_profile_name = None
  username = None
  password = None
  server_ip = None
  install_credential_name = None
  install_credential_username = None
  install_credential_key = None
  cassandra_default_password = None

  node_sync: List[NodeSyncConfiguration] = None
  config_profiles: List[ConfigProfileConfiguration] = None
  datacenter_configuration: List[DatacenterConfiguration] = None

  def load_config(self, config_file):
    # .config/config.yaml
    try:
      if not config_file:
        config = configparser.get_config(SCHEMA_CONFIG)
      else:
        config = configparser.get_config(SCHEMA_CONFIG, config_dir='', file_name=config_file)

      self.username = config['opscenter']['opscenter_username']
      self.password = config['opscenter']['opscenter_password']
      self.server_ip = config['opscenter']['opscenter_server_ip']

      self.config_profile_name = config['cluster']['config_profile_name']

      self.cluster_name = config['dse']['cluster_name']
      self.datastax_version = config['dse']['datastax_version']
      self.repository_name = config['dse']['repository_name']
      self.install_credential_name = config['dse']['install_credential_name']
      self.install_credential_username = config['dse']['install_credential_username']
      self.cassandra_default_password = config['dse']['cassandra_default_password']

      # SSH key
      with open(config['dse']['install_credential_key_file'], 'r') as key_file:
        self.install_credential_key = key_file.read()

      # Initialise config profiles
      if 'config_profiles' in config:
        profiles = []
        for config_profile in config['config_profiles']:
          profiles += [
            ConfigProfileConfiguration(
                config_profile['name'],
                cassandra_yaml=config_profile['cassandra_yaml'] if 'cassandra_yaml' in config_profile else None,
                cassandra_env_sh=config_profile['cassandra_env_sh'] if 'cassandra_env_sh' in config_profile else None,
                dse_env_sh=config_profile['dse_env_sh'] if 'dse_env_sh' in config_profile else None
            )
          ]
        self.config_profiles = profiles

      if 'node_sync' in config:
        node_sync_tables = []
        for node_sync in config['node_sync']:
          node_sync_tables += [NodeSyncConfiguration(node_sync['pattern'])]
        self.node_sync = node_sync_tables

      # Initialise datacenter configurations
      datacenters = []
      for datacenter in config['cluster']['datacenters']:
        nodes = []
        for node in datacenter['nodes']:
          nodes += [NodeConfiguration(
              node['name'],
              node['private_ip'],
              node['node_ip'],
              node['rack'],
              node['config_profile_name'] if 'config_profile_name' in node else None
          )]

        datacenters += [DatacenterConfiguration(
            datacenter['name'],
            datacenter['solr_enabled'],
            datacenter['spark_enabled'],
            datacenter['graph_enabled'],
            datacenter['hadoop_enabled'],
            nodes,
            config_profile_name=datacenter['config_profile_name'] if 'config_profile_name' in datacenter else None,
        )]
      self.datacenter_configuration = datacenters
    except ConfigError as e:
      print(e)
      exit()

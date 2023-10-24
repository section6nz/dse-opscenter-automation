import logging
import json

import common
from config import OpsCenterConfiguration, ConfigProfileConfiguration


def load_config_profiles(session_id, config: OpsCenterConfiguration):
  config_profile_dict = dict()
  config_profiles_list = common.do_get(config, session_id, 'config_profiles/')
  for profile in config_profiles_list['results']:
    config_profile_dict[profile['name']] = profile['id']

  return config_profile_dict


def create_config_profile(session_id, config: OpsCenterConfiguration, config_profile: ConfigProfileConfiguration):
  config_profile_id = None
  config_profiles_list = common.do_get(config, session_id, 'config_profiles/')
  for profile in config_profiles_list['results']:
    if profile['name'] == config_profile.name:
      logging.warning("Config profile already exists, skipping creation. config_profile_name: %s",
                      config_profile.name)
      config_profile_id = profile['id']

  if not config_profile_id:
    config_profile_response = common.do_post(
        config,
        session_id,
        "config_profiles/",
        {"name": config_profile.name,
         "datastax-version": config.datastax_version,
         'json': {
           "cassandra-env-sh": json.loads(config_profile.cassandra_env_sh) if config_profile.cassandra_env_sh else {},
           "cassandra-yaml": json.loads(config_profile.cassandra_yaml) if config_profile.cassandra_yaml else {},
           "dse-env-sh": json.loads(config_profile.dse_env_sh) if config_profile.dse_env_sh else {},
           "dse-yaml": json.loads(config_profile.dse_yaml) if config_profile.dse_yaml else {}
         },
         "comment": 'LCM provisioned as %s' % config.config_profile_name}
    )

    config_profile_id = config_profile_response['id']
    logging.info("Created config profile, config_profile_id: %s", config_profile_id)

  return config_profile_id

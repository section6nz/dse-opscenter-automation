import logging

import common
from config import OpsCenterConfiguration


def create_repo(session_id, config: OpsCenterConfiguration):
    repo_id = None
    repository_list = common.do_get(config, session_id, 'repositories/')
    for repo in repository_list['results']:
        if repo['name'] == config.repository_name:
            logging.warning("Repository already exists, skipping creation. repo_name: %s", config.repository_name)
            repo_id = repo['id']

    if not repo_id:
        repository_response = common.do_post(
            config,
            session_id,
            "repositories/",
            {
                "name": config.install_credential_name,
                "use-proxy": True,
                "comment": "Created from python"
            })

        repo_id = repository_response['id']
        logging.info("Created repository, repository_id: %s", repo_id)

    return repo_id

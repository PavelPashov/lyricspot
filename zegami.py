import logging
import os
import subprocess
import time
import requests
import re

from flask import session

from tempfile import NamedTemporaryFile

YAML_CONF = """
name: {name}
description: Spotify Top 50 Tracks
enable_clustering: True
imageset_type: url
dataset_column: image_link
url_template: {url_template}
image_fetch_headers:
    Accept: image/jpg
dataset_type: file
file_config:
    path: {datafile_path}
"""

PUBLISH_CONF = """
update_type: publish
publish_config:
    publish: True
    destination_project: public
"""

zeg_token = os.environ.get("ZEGAMI_TOKEN")


def create_yaml_file(name=None, datafile_path=None):

    file_contents = ''
    if name:
        file_contents = YAML_CONF.format(
            name=name,
            url_template="'{}'",
            datafile_path=datafile_path,
        )
    else:
        file_contents = PUBLISH_CONF.format()

    yaml_file = NamedTemporaryFile(
        suffix=".yaml", mode="w+t", delete=False)

    yaml_file.write(file_contents)
    yaml_file.close()

    return yaml_file.name


def create_collection(yaml_path):
    """Create the collection and return the output."""

    command = ['zeg', 'create', 'collections',
               '--project', 'pv5ed2jm', '--config',
               yaml_path, '--url', 'https://staging.zegami.com/', '--token', zeg_token]

    output = subprocess.run(
        command, stdout=subprocess.PIPE).stdout.decode('utf-8')
    return output


def get_coll_id(output):
    """Get the collection creation output and return the collecion's id."""
    coll_id_re = re.compile(r'  id:.(\d\w+)')
    coll_id = re.search(coll_id_re, output).group(1)
    return coll_id


def publish_coll(coll_id):
    try:
        yaml_path = create_yaml_file()
        command = ['zeg', 'publish', 'collection', coll_id,
                   '--project', 'pv5ed2jm', '--config',
                   yaml_path, '--url', 'https://staging.zegami.com/', '--token', zeg_token]
        subprocess.run(command)
        session['is_published'] = True
        os.remove(yaml_path)
    except Exception as e:
        logging.error(e, exc_info=True)
        return None


def delete_file(files):
    for file in files:
        try:
            os.remove(file)
        except Exception as e:
            logging.error(e, exc_info=True)
            return None


def check_progress(coll_id, project='pv5ed2jm'):
    url_request = f'https://staging.zegami.com/api/v0/project/{project}/collections/' + coll_id
    try:
        response = requests.get(url_request, headers={'Authorization': f'Bearer {zeg_token}'})
        progress = response.json()["collection"]["status"]["progress"]
        return progress
    except Exception as e:
        logging.error(e, exc_info=True)
        return None

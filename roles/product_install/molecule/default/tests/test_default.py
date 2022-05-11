import os
from six.moves import urllib

import testinfra.utils.ansible_runner
import json

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_version_file_is_latest(host):
    verfile = host.file('/media/atl/jira/shared/jira-core.version')
    assert verfile.exists

    upstream_fd = urllib.request.urlopen("https://marketplace.atlassian.com/rest/2/products/key/jira-software/versions")
    upstream_json = json.load(upstream_fd)
    upstream = upstream_json['_embedded']['versions'][0]['name']

    assert verfile.content.decode("UTF-8").strip() == upstream.strip()

def test_latest_is_downloaded(host):
    upstream_fd = urllib.request.urlopen("https://marketplace.atlassian.com/rest/2/products/key/jira-software/versions")
    upstream_json = json.load(upstream_fd)
    upstream = upstream_json['_embedded']['versions'][0]['name']

    installer = host.file('/media/atl/downloads/jira-core.'+upstream+'-x64.bin')
    assert installer.exists
    assert installer.user == 'root'

def test_completed_lockfile(host):
    upstream_fd = urllib.request.urlopen("https://marketplace.atlassian.com/rest/2/products/key/jira-software/versions")
    upstream_json = json.load(upstream_fd)
    upstream = upstream_json['_embedded']['versions'][0]['name']

    lockfile = host.file('/media/atl/downloads/jira-core.'+upstream+'-x64.bin_completed')
    assert lockfile.exists
    assert lockfile.user == 'root'

def test_servicedesk_not_installed(host):
    plugins = host.file('/media/atl/jira/shared/plugins/installed-plugins')
    assert (not plugins.exists) or (len(list(filter(lambda p: 'servicedesk' in p, jars))) == 0)

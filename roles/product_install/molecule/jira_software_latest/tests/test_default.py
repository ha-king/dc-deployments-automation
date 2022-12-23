import os
from six.moves import urllib

import testinfra.utils.ansible_runner
import json

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

def test_version_downloaded(host):
    verfile = host.file('/media/atl/jira/shared/jira-software.version')
    assert verfile.exists

def test_symlink_created(host):
    target = host.file('/opt/atlassian/jira-software/current')
    assert target.exists
    assert target.is_symlink

def test_unpacked(host):
    verfile = host.file('/opt/atlassian/jira-software/current/bin/catalina.sh')
    assert verfile.exists

def test_version_file_is_latest(host):
    verfile = host.file('/media/atl/jira/shared/jira-software.version')
    assert verfile.exists

    upstream_fd = urllib.request.urlopen("https://marketplace-admin.internal.atlassian.com/rest/2/products/key/jira-software/versions")
    upstream_json = json.load(upstream_fd)
    upstream = upstream_json['_embedded']['versions'][0]['name']

    assert verfile.content.decode("UTF-8").strip() == upstream.strip()

def test_latest_is_downloaded(host):
    upstream_fd = urllib.request.urlopen("https://marketplace-admin.internal.atlassian.com/rest/2/products/key/jira-software/versions")
    upstream_json = json.load(upstream_fd)
    upstream = upstream_json['_embedded']['versions'][0]['name']

    installer = host.file('/media/atl/downloads/jira-software.'+upstream+'-x64.bin')
    assert installer.exists
    assert installer.user == 'root'

def test_completed_lockfile(host):
    upstream_fd = urllib.request.urlopen("https://marketplace-admin.internal.atlassian.com/rest/2/products/key/jira-software/versions")
    upstream_json = json.load(upstream_fd)
    upstream = upstream_json['_embedded']['versions'][0]['name']

    lockfile = host.file('/media/atl/downloads/jira-software.'+upstream+'-x64.bin_completed')
    assert lockfile.exists
    assert lockfile.user == 'root'
import os
import json
from six.moves import urllib

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

def get_latest():
    data = urllib.request.urlopen("https://marketplace-admin.internal.atlassian.com/rest/2/products/key/jira-servicedesk/versions/latest")
    meta = json.loads(data.read().decode("UTF-8"))
    servicedesk = meta['name']
    jira = meta['compatibilities'][0]['hosting']['server']['max']['version']
    return (servicedesk, jira)

(sd, jira) = get_latest()

def test_version_is_correct(host):
    verfile = host.file('/media/atl/jira/shared/jira-servicedesk.version')
    assert verfile.exists

    assert verfile.content.decode("UTF-8").strip() == sd

def test_is_downloaded(host):
    installer = host.file('/media/atl/downloads/servicedesk.'+sd+'-x64.bin')
    assert installer.exists
    assert installer.user == 'root'

def test_completed_lockfile(host):
    lockfile = host.file('/media/atl/downloads/servicedesk.'+sd+'-x64.bin_completed')
    assert lockfile.exists
    assert lockfile.user == 'root'

def test_is_unpacked(host):
    installer = host.file('/opt/atlassian/jira-servicedesk/'+sd)
    assert installer.exists
    assert installer.is_directory
    assert installer.user == 'jira'

def test_plugin_is_present(host):
    installer = host.file('/opt/atlassian/jira-servicedesk/current/atlassian-jira/WEB-INF/application-installation/jira-servicedesk-application/jira-servicedesk-application-'+sd+'.jar')
    assert installer.exists
    assert installer.user == 'jira'

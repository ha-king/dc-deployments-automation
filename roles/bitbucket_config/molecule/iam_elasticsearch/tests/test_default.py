import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_config_file(host):
    f = host.file('/media/atl/bitbucket/shared/bitbucket.properties')
    assert f.exists

    assert not f.contains("plugin.search.config.username")
    assert not f.contains("plugin.search.config.password")
    assert f.contains("plugin.search.config.aws.region=us-east-2")

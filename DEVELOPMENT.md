## Prerequisites

You should have the following software installed:
* Python; 3.8 or newer
  * You may also need the Python development packages depending on how it’s installed
  * Note that the runtime still requires Python 2 for certain tasks on Amazon Linux 2, but is not necessary for local development
* Python Virtualenv
* Docker
* Cloudtoken

All other requirements will be installed under Virtualenv.

## Step 1: Install and test the playbooks locally

### Step 1.1: Get the repo

    git clone git@bitbucket.org:atlassian/dc-deployments-automation.git

### Step 1.2: Install development environment dependencies

To ensure compatibility we specify a specific Ansible version; currently
ansible-core 2.13.x. We do this with [Pipenv](https://docs.pipenv.org/) to lock
the dependency tree. There are 2 main ways to do this; either directly if
packaged, or via pip...

    # Ubuntu 22.04+, Debian 11+
    sudo apt-get install python3-dev python3-pip

    # Amazon Linux 2
    sudo amazon-linux-extras enable python3.8
    sudo yum install python38 python38-pip python38-devel python-lxml

    # Mac via Homebrew
    brew install libpq openssl@3 python@X.x  # (where "X.x") is 3.8 or newer
    export PATH="/opt/homebrew/opt/libpq/bin:$PATH"
    export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
    export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"

    # Finally
    pip3 install pipenv

### Step 1.3: Enter the development environment

pipenv has 2 methods of entering the environment; `pipenv shell` and `pipenv
run`. As we need additional testing dependencies we all need to specify the
development environment:

    pipenv sync --dev
    pipenv shell --dev

### Step 1.4: Install Ansible collections

To save a little time during deployment, we rely directly on ansible-core and a
custom set of collections as opposed to installing the community edition. To that
end, when testing locally, you'll need these collections installed where Ansible
expects them to be; that path is configured ansible.cfg and used automatically
when collections are installed via `ansible-galaxy`:

    ansible-galaxy collection install --upgrade --verbose --requirements-file requirements.yml

### Step 1.5: Run some tests against a role

[Molecule](https://molecule.readthedocs.io/en/stable/) is a testing framework for
Ansible. We use this to test the functionality of individual and groups of roles,
and to ensure cross-platform compatibility (currently Amazon Linux 2 and Ubuntu LTS).

We’re going to check that the role that downloads the products works for both
Jira Core and Confluence, on boths supported Linux distributions. So run the
following:

    cd roles/product_install/
    molecule test -s jira_version_latest
    molecule test -s servicedesk3

This starts Docker containers for each distro, runs the playbook in
molecule/<scenario>/playbook.yml and runs testinfra tests against the
results. In practice, when developing roles is better to run molecule create -s
<scenario> and then molecule converge -s <scenario> repeatedly do iteratively
develop.

## Step 2: Test out the playbook with AWS Cloudformation

### Step 2.1: Get the updated Cloudformation template

There is a slightly modified version for the official Atlassian Jira Quickstart
that uses the baseline Amazon Linux 2 AMI and Ansible. The branch containing the
changes is in the Atlassian Github fork of the upstream repository, in the
branch DCD-221-jira-dc-linux2-ansible-rework.

### Step 2.2: Setup taskcat

Taskcat is a tool for testing Cloudformation templates. It is generally the
simplest method of getting a template up and running from local changes. It is
automatically installed as part of the pipenv environment.

You may also need to create the file ~/.aws/taskcat_global_override.json and set
the KeyPair parameter to access the deployed EC2 instances. See the taskcat docs
for details.

### Step 2.3: Configure and deploy your Jira instance with Cloudformation and Ansible

You should probably modify some of the parameters, as we want to do some manual testing:

* Edit ci/taskcat.yml and update the region (last line). You will need to select
  a region that does not have another quickstart running it.
* Edit ci/quickstart-jira-dc-params.json and modify the following:
 * Set AssociatePublicIpAddress to true.
 * Set CidrBlock and AccessCIDR to 0.0.0.0/0.
 * If you want to test any other deployment parameters with the Ansible playbook
   this is where to modify them.

To deploy the modified Cloudformation template, refresh your AWS keys with
cloudtoken, and run:

    taskcat -c ci/taskcat -n

*NOTE*: The -n flag disables teardown of the instance, so you must do this yourself via
the Cloudformation console.

### Step 2.4: Configure and verify the installed Jira instance

The output of the Cloudformation template included the URL of the deployed
load-balancer. Access this to finalise the configuration and install a license.

You may also want to use the EC2 console to enable clustering after
configuration, and create and destroy cluster nodes.

### Step 2.5: Accessing logs, and looking around inside the deployed node

To manually inspect the deployed Jira nodes, do the following:

* Fetch the bastion public IP address from either template output, or the EC2
  console.
* Login to it with ssh ec2-user@<ip-address>.
* Get the node internal IP address from the EC2 console
* Login to the node with ssh <ip-address>.
* Change to root with sudo -i

Some notable files and locations:

* The output cfn-init is under /var/log/cfn-init.log .
* The output of the Ansible playbook is in there, and also
  /var/log/ansible-bootstrap.log.
* The Jira installation is under /opt/atlassian/jira/<version>and symlinked to
  /opt/atlassian/jira/current.
* The systemd service is configured in /usr/lib/systemd/system/jira.service. Its
  stdout can be viewed with systemctl status jira.service and journalctl -u
  jira.service.
* Other Tomcat logs can be located under /opt/atlassian/jira/current/logs/...

## Running molecule tests on CI
* This repository is configured to run tests on [bitbucket pipelines](https://bitbucket.org/atlassian/dc-deployments-automation/addon/pipelines/home).
    * Pipeline definition is located in the [root of the repository](https://bitbucket.org/atlassian/dc-deployments-automation/src/master/bitbucket-pipelines.yml)
    * Pipeline configuration is generated using Jinja2 and a simple python script. Pipeline generator is located [here](https://bitbucket.org/atlassian/dc-deployments-automation/src/master/pipeline_generator/)
    * A pipeline configuration is generated by running the following make command
    ```
     make generate-pipeline > ../bitbucket-pipelines.yml
    ```

* [Molecule](https://molecule.readthedocs.io/en/stable/) tests are run in batches. A single test is run per batch to optimize for a faster dev feedback loop

* If you create a new role or add a new molecule scenario, then please ensure that you generate a new pipeline configuration by running the make command described above. If a new pipeline configuration is not generated, then the CI may not run any tests as it would fail at a pre-test validate stage.
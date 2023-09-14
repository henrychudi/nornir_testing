from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.data import load_yaml
from nornir_jinja2.plugins.tasks import template_file
from nornir_scrapli.tasks import (
    netconf_edit_config,
    netconf_commit,
    netconf_lock,
    netconf_unlock,
)

nr = InitNornir(config_file="config.yaml")


def load_vars(task):
    """
    Load host variables and bind them to a per-host dict key called "facts"
    """

    data = task.run(
        task=load_yaml,
        name="Loading Vars Into Memory...",
        file=f"./host_vars/{task.host}.yaml",
    )
    task.host["facts"] = data.result


def lock_config(task):
    task.run(task=netconf_lock, target="running", name="Locking...")


def config_router(task):
    """
    Build INTERFACE config based on IOS-XE YANG Model
    Push configuration over NETCONF
    """

    router_template = task.run(
        task=template_file,
        name="Buildling BGP Configuration",
        template="router.j2",
        path="./templates",
    )
    router_output = router_template.result
    task.run(
        task=netconf_edit_config,
        name="Automating BGP",
        target="running",
        config=router_output,
    )

def config_segment(task):
    """
    Build SEGMENT ROUTING config based on IOS-XE YANG Model
    Push configuration over NETCONF
    """

    segment_routing_template = task.run(
        task=template_file,
        name="Buildling BGP Configuration",
        template="segment.j2",
        path="./templates",
    )
    segment_routing_output = segment_routing_template.result
    task.run(
        task=netconf_edit_config,
        name="Automating SR",
        target="running",
        config=segment_routing_output,
    )


def unlock_config(task):
    task.run(task=netconf_unlock, target="candidate")

# DON'T COMMENT THIS ONE OUT - THIS LOADS THE VARIABLE DATA
var = nr.run(task=load_vars)
print_result(var)

# DON'T COMMENT THIS ONE OUT - THIS LOCKS THE CONFIGURATION DATASTORE
locker = nr.run(task=lock_config, name="NETCONF_LOCK")
print_result(locker)

# COMMENT THIS OUT IF YOU WANT TO SKIP BGP CONFIG
router_results = nr.run(task=config_router, name="INTERFACE CONFIGURATION")
print_result(router_results)

# COMMENT THIS OUT IF YOU WANT TO SKIP SR CONFIG
SR_results = nr.run(task=config_segment, name="SEGMENT ROUTING CONFIGURATION")
print_result(SR_results)

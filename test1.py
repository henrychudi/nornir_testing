from nornir_scrapli.tasks import netconf_get
from nornir_utils.plugins.functions import print_result
from nornir import InitNornir
from xml.dom import minidom

nr = InitNornir(config_file="config.yaml")

def netconf_test(task):
    result = task.run(task=netconf_get, filter_ = "/native/router", filter_type="xpath")

result = nr.run(task=netconf_test)
print_result(result)

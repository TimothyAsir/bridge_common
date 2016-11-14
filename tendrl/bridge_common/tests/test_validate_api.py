"""
test_validate_api
----------------------------------

Tests for `validate_api` module.
"""

import os
import sys

#sys.path.insert(0, '../')
sys.path.append('../..')
from bridge_common.definitions.validator import JobValidator
from bridge_common import util


def getSchemaFile(schemaName):
    localpath = os.path.dirname(__file__)
    path = os.path.join(localpath, "sds_state_" + schemaName + '.yaml')
    # return yaml.load(open(path))
    return util.loadSchema(path)


class TestValidateJobApi(object):

    def test_validate(self):
        # Success test
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_name": "gluster",
            "sds_version": "3.2.0",
            "flow": "namespace.tendrl.gluster_bridge.gluster_integration.flows.CreateGlusterVolume",
            "status": "processing",
            "parameters": {
                'volname': 'Volume1',
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
        }
        sdsoper = JobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.validateApi(glusterApiJob)
        assert status

    def test_atom(self):
        sdsoper = JobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.checkAtom("volume.atoms.start", sdsoper.objects)
        assert error == "object atom details not found for:volume"
        assert not status

    def test_flow(self):
        sdsoper = JobValidator(getSchemaFile("gluster"))
        jobFlow = "namespace.tendrl.gluster_bridge.gluster_integration.flows.StartVolume"
        namespace = sdsoper.definitions[jobFlow.split("flows")[0].strip(".")]
        flow_class_name = jobFlow.split("flows")[-1].strip(".")
        flow = namespace['flows'].get(flow_class_name)
        status, error = sdsoper.checkFlow(flow)
        assert status == True

        jobFlow = "namespace.tendrl.gluster_bridge.gluster_integration.flows.StopVolume"
        namespace = sdsoper.definitions[jobFlow.split("flows")[0].strip(".")]
        flow_class_name = jobFlow.split("flows")[-1].strip(".")
        flow = namespace['flows'].get(flow_class_name)
        assert flow == None

    def test_getFlowParm(self):
        sdsoper = JobValidator(getSchemaFile("gluster"))
        jobFlow = "namespace.tendrl.gluster_bridge.gluster_integration.flows.CreateGlusterVolume"
        namespace = sdsoper.definitions[jobFlow.split("flows")[0].strip(".")]
        flow_class_name = jobFlow.split("flows")[-1].strip(".")
        flow = namespace['flows'].get(flow_class_name)
        reqParm, optParm = sdsoper.getFlowParms(flow)
        print reqParm, optParm
        assert set(reqParm) ==  set(['Volume.volname', 'Volume.brickdetails'])

    def test_checkJobRequiredAttr(self):
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_name": "gluster",
            "sds_version": "3.2.0",
            "flow": "namespace.tendrl.gluster_bridge.gluster_integration.flows.CreateGlusterVolume",
            "status": "processing",
            "parameters": {
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
        }
        sdsoper = JobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.checkJobRequiredParm(
            glusterApiJob['parameters'], ['volname', 'brickdetails'])
        assert error == "Missing input argument(s) ['volname']"

    def test_apijob_with_wrong_datatype(self):
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_name": "gluster",
            "sds_version": "3.2.0",
            "flow": "namespace.tendrl.gluster_bridge.gluster_integration.flows.CreateGlusterVolume",
            "status": "processing",
            "parameters": {
                'volname': 'Volume1',
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
            'errors': {}
        }
        sdsoper = JobValidator(getSchemaFile("gluster"))
        # Testing with invalid data type for strip_count
        glusterApiJob['parameters']['stripe_count'] = '10'
        status, error = sdsoper.validateApi(glusterApiJob)
        msg = "Invalid parameter type: stripe_count. "\
              "Expected value type is: Integer"
        assert error == msg
        assert not status

        glusterApiJob['parameters']['stripe_count'] = []
        status, error = sdsoper.validateApi(glusterApiJob)
        msg = "Invalid parameter type: stripe_count. "\
              "Expected value type is: Integer"
        assert error == msg
        assert not status

        glusterApiJob['parameters']['stripe_count'] = "RAID"
        status, error = sdsoper.validateApi(glusterApiJob)
        msg = "Invalid parameter type: stripe_count. "\
              "Expected value type is: Integer"
        assert error == msg
        assert not status

    def test_apijob_without_required_arguments(self):
        # Volume name not provided
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_name": "gluster",
            "sds_version": "3.2.0",
            "flow": "namespace.tendrl.gluster_bridge.gluster_integration.flows.CreateGlusterVolume",
            "status": "processing",
            "parameters": {
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
        }
        sdsoper = JobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error == "Missing input argument(s) ['volname']"
        assert not status

        glusterApiJob['parameters'].pop('stripe_count')
        status, error = sdsoper.validateApi(glusterApiJob)
        # stripe_count is an optional param
        assert error == "Missing input argument(s) ['volname']"
        assert not status

    def test_apijob_with_wrong_argument_name(self):
        # Invalid argument names passed which are not defined
        glusterApiJob = {
            'cluster_id': "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "sds_name": "gluster",
            "sds_version": "3.2.0",
            "flow": "namespace.tendrl.gluster_bridge.gluster_integration.flows.CreateGlusterVolume",
               "status": "processing",
            "parameters": {
                'myvolumename': 'testing',
                'volname': "test",
                'blabla': 100,
                'stripe_count': 10,
                'brickdetails': ['/mnt/brick1', '/mnt/brick2']},
            'errors': {}
        }
        sdsoper = JobValidator(getSchemaFile("gluster"))
        status, error = sdsoper.validateApi(glusterApiJob)
        assert error.find("argument(s) not defined") > 0
        assert error.find('myvolumename') > 0
        assert error.find('blabla') > 0
        assert not status

    def test_apijob_missing_argument(self):
        nodeApiJob = {
            "cluster_id": "bc35fde8-528b-4908-8d52-50d8bf964dd4",
            "node_uuid": "node_uuid",
            "flow": "namespace.tendrl.node_agent.gluster_integration.flows.ImportCluster",
            "status": "processing",
            "parameters": {
                'sds_version': "3.0",
                'sds_name': "node",
                'Node': [{'fqdn': "abc.12.com", 'cmd_str': 'install'},
                         {'fqdn': "xyz.com", 'cmd_str': 'execute'}]
            }
        }
        sdsoper = JobValidator(getSchemaFile("node"))
        status, error = sdsoper.validateApi(nodeApiJob)
        assert status == True

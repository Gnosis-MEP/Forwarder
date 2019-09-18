from unittest.mock import patch

from event_service_utils.tests.base_test_case import MockedServiceStreamTestCase
from event_service_utils.tests.json_msg_helper import prepare_event_msg_tuple

from forwarder.service import Forwarder

from forwarder.conf import (
    SERVICE_STREAM_KEY,
    SERVICE_CMD_KEY,
)


class TestForwarder(MockedServiceStreamTestCase):
    GLOBAL_SERVICE_CONFIG = {
        'service_stream_key': SERVICE_STREAM_KEY,
        'service_cmd_key': SERVICE_CMD_KEY,
        'logging_level': 'ERROR'
    }
    SERVICE_CLS = Forwarder
    MOCKED_STREAMS_DICT = {
        SERVICE_STREAM_KEY: [],
        SERVICE_CMD_KEY: [],
    }

    @patch('forwarder.service.Forwarder.process_action')
    def test_process_cmd_should_call_process_action(self, mocked_process_action):
        action = 'someAction'
        event_data = {
            'action': action,
            'some': 'stuff'
        }
        msg_tuple = prepare_event_msg_tuple(event_data)

        self.service.service_cmd.mocked_values = [msg_tuple]
        self.service.process_cmd()
        self.assertTrue(mocked_process_action.called)
        self.service.process_action.assert_called_once_with(action, event_data, msg_tuple[1])

    @patch('forwarder.service.Forwarder.add_query')
    def test_process_action_should_call_process_action_addQuery(self, mocked_add_query):
        action = 'addQuery'
        query_data = {
            'subscriber_id': 'sub-id',
            'query_id': '44d7985a',
            'publisher_id': '44d7985b',
        }
        event_data = query_data.copy()
        event_data.update({
            'action': action,
        })
        msg_tuple = prepare_event_msg_tuple(event_data)

        self.service.service_cmd.mocked_values = [msg_tuple]
        self.service.process_cmd()
        self.assertTrue(mocked_add_query.called)
        mocked_add_query.assert_called_once_with(
            query_data['subscriber_id'],
            query_data['query_id'],
            query_data['publisher_id'],
        )

    @patch('forwarder.service.Forwarder.del_query')
    def test_process_action_should_call_process_action_delQuery(self, mocked_add_query):
        action = 'delQuery'
        query_data = {
            'query_id': '44d7985a',
        }
        event_data = query_data.copy()
        event_data.update({
            'action': action,
        })
        msg_tuple = prepare_event_msg_tuple(event_data)

        self.service.service_cmd.mocked_values = [msg_tuple]
        self.service.process_cmd()
        self.assertTrue(mocked_add_query.called)
        mocked_add_query.assert_called_once_with(
            query_data['query_id'],
        )

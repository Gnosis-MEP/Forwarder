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
        'logging_level': 'ERROR',
        'tracer_configs': {'reporting_host': None, 'reporting_port': None},
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
            'id': 1,
            'action': action,
            'some': 'stuff'
        }
        msg_tuple = prepare_event_msg_tuple(event_data)
        mocked_process_action.__name__ = 'process_action'

        self.service.service_cmd.mocked_values = [msg_tuple]
        self.service.process_cmd()
        self.assertTrue(mocked_process_action.called)
        self.service.process_action.assert_called_once_with(action=action, event_data=event_data, json_msg=msg_tuple[1])

    @patch('forwarder.service.Forwarder.add_query')
    def test_process_action_should_call_process_action_addQuery(self, mocked_add_query):
        action = 'addQuery'
        query_data = {
            'id': 1,
            'query_id': 'query_id',
            'subscriber_id': 'subscriber_id',
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
        )

    @patch('forwarder.service.Forwarder.del_query')
    def test_process_action_should_call_process_action_delQuery(self, mocked_add_query):
        action = 'delQuery'
        query_data = {
            'id': 1,
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

    def test_forward_to_query_ids_stream_should_send_events_to_all_stream(self):
        event_data = {
            'id': '1',
            'query_id': 'query-id1',
            'vekg_stream': [{'event': 1}, {'event': 2}]
        }
        self.stream_factory.mocked_dict['query-id1'] = []
        self.service.forward_to_query_ids_stream(event_data)
        self.assertEqual(len(self.stream_factory.mocked_dict['query-id1']), 2)

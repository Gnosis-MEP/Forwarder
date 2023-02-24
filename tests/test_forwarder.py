from unittest.mock import patch

from event_service_utils.tests.base_test_case import MockedEventDrivenServiceStreamTestCase
from event_service_utils.tests.json_msg_helper import prepare_event_msg_tuple

from forwarder.service import Forwarder

from forwarder.conf import (
    SERVICE_STREAM_KEY,
    SERVICE_CMD_KEY_LIST,
    SERVICE_DETAILS,
    PUB_EVENT_LIST,
)


class TestForwarder(MockedEventDrivenServiceStreamTestCase):
    GLOBAL_SERVICE_CONFIG = {
        'service_stream_key': SERVICE_STREAM_KEY,
        'service_cmd_key_list': SERVICE_CMD_KEY_LIST,
        'pub_event_list': PUB_EVENT_LIST,
        'service_details': SERVICE_DETAILS,
        'logging_level': 'ERROR',
        'tracer_configs': {'reporting_host': None, 'reporting_port': None},
    }
    SERVICE_CLS = Forwarder
    MOCKED_CG_STREAM_DICT = {

    }
    MOCKED_STREAMS_DICT = {
        SERVICE_STREAM_KEY: [],
        'cg-Forwarder': MOCKED_CG_STREAM_DICT,
    }

    @patch('forwarder.service.Forwarder.process_event_type')
    def test_process_cmd_should_call_process_event_type(self, mocked_process_event_type):
        event_type = 'SomeEventType'
        unicode_event_type = event_type.encode('utf-8')
        event_data = {
            'id': 1,
            'action': event_type,
            'some': 'stuff'
        }
        msg_tuple = prepare_event_msg_tuple(event_data)
        mocked_process_event_type.__name__ = 'process_event_type'

        self.service.service_cmd.mocked_values_dict = {
            unicode_event_type: [msg_tuple]
        }
        self.service.process_cmd()
        self.assertTrue(mocked_process_event_type.called)
        self.service.process_event_type.assert_called_once_with(event_type=event_type, event_data=event_data, json_msg=msg_tuple[1])

    @patch('forwarder.service.Forwarder.add_query')
    def test_process_event_type_should_call_process_action_addQuery(self, mocked_add_query):
        parsed_query = {
            'from': ['pub1'],
            'content': ['ObjectDetection', 'ColorDetection'],
            'window': {
                'window_type': 'TUMBLING_COUNT_WINDOW',
                'args': [2]
            },
            'match': "MATCH (c1:Car {color:'blue'}), (c2:Car {color:'white'})",
            'optional_match': 'optional_match',
            'where': 'where',
            'ret': 'RETURN *',
            # 'cypher_query': query['cypher_query'],
        }
        event_data = {
            'id': 1,
            'query_id': 'query-id',
            'subscriber_id': 'subscriber_id',
            'parsed_query': parsed_query,
        }
        event_type = 'QueryCreated'
        json_msg = prepare_event_msg_tuple(event_data)[1]
        self.service.process_event_type(event_type, event_data, json_msg)
        self.assertTrue(mocked_add_query.called)
        mocked_add_query.assert_called_once_with(
            event_data['subscriber_id'],
            event_data['query_id'],
        )

    @patch('forwarder.service.Forwarder.del_query')
    def test_process_action_should_call_process_action_delQuery(self, mocked_add_query):
        parsed_query = {
            'from': ['pub1'],
            'content': ['ObjectDetection', 'ColorDetection'],
            'window': {
                'window_type': 'TUMBLING_COUNT_WINDOW',
                'args': [2]
            },
            'match': "MATCH (c1:Car {color:'blue'}), (c2:Car {color:'white'})",
            'optional_match': 'optional_match',
            'where': 'where',
            'ret': 'RETURN *',
            # 'cypher_query': query['cypher_query'],
        }
        event_data = {
            'id': 1,
            'query_id': 'query-id',
            'subscriber_id': 'subscriber_id',
            'parsed_query': parsed_query,
            'deleted': True,
        }
        event_type = 'QueryRemoved'
        json_msg = prepare_event_msg_tuple(event_data)[1]
        self.service.process_event_type(event_type, event_data, json_msg)
        self.assertTrue(mocked_add_query.called)
        mocked_add_query.assert_called_once_with(
            event_data['query_id'],
        )

    def test_forward_to_query_ids_stream_should_send_events_to_all_stream(self):
        event_data = {
            'id': '1',
            'query_id': 'query-id1',
            'vekg_stream': [{'event': 1}, {'event': 2}]
        }
        self.stream_factory.mocked_dict['query-id1'] = []
        self.service.forward_to_query_ids_stream(event_data)
        self.assertEqual(len(self.stream_factory.mocked_dict['query-id1']), 1)

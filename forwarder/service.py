import threading

from event_service_utils.services.base import BaseService
from event_service_utils.schemas.internal_msgs import (
    BaseInternalMessage,
)

from forwarder.schemas import load_event_data, event_data_to_json


class Forwarder(BaseService):
    def __init__(self,
                 service_stream_key, service_cmd_key,
                 stream_factory,
                 logging_level):

        super(Forwarder, self).__init__(
            name=self.__class__.__name__,
            service_stream_key=service_stream_key,
            service_cmd_key=service_cmd_key,
            cmd_event_schema=BaseInternalMessage,
            stream_factory=stream_factory,
            logging_level=logging_level
        )
        self.query_id_to_subscriber_id_map = {}

    def get_destination_streams(self, destination):
        return self.stream_factory.create(destination, stype='streamOnly')

    def forward_to_query_ids_stream(self, event_data):
        json_msg = event_data_to_json(event_data)
        query_ids = event_data.get('query_ids', [])
        self.logger.debug('Sending {event_data} to {query_ids} streams')
        for query_id in query_ids:
            self.get_destination_streams(query_id).write_events(json_msg)

    def forward_to_final_stream(self, event_data):
        self.forward_to_query_ids_stream(event_data)

    def add_query(self, subscriber_id, query_id):
        self.query_id_to_subscriber_id_map[query_id] = subscriber_id

    def del_query(self, query_id):
        self.query_id_to_subscriber_id_map.pop(query_id, None)

    def process_data(self):
        self.logger.debug('Processing DATA..')
        if not self.service_stream:
            return
        event_list = self.service_stream.read_events(count=1)
        for event_tuple in event_list:
            event_id, json_msg = event_tuple
            event_data = load_event_data(json_msg)
            self.logger.debug(f'Processing new data: {event_data}')
            self.forward_to_final_stream(event_data)

    def process_action(self, action, event_data, json_msg):
        super(Forwarder, self).process_action(action, event_data, json_msg)
        if action == 'addQuery':
            subscriber_id = event_data['subscriber_id']
            query_id = event_data['query_id']
            self.add_query(subscriber_id, query_id)
        elif action == 'delQuery':
            query_id = event_data['query_id']
            self.del_query(query_id)

    def log_state(self):
        super(Forwarder, self).log_state()
        self._log_dict('Query to Subscriber ids', self.query_id_to_subscriber_id_map)

    def run(self):
        super(Forwarder, self).run()
        self.cmd_thread = threading.Thread(target=self.run_forever, args=(self.process_cmd,))
        self.data_thread = threading.Thread(target=self.run_forever, args=(self.process_data,))
        self.cmd_thread.start()
        self.data_thread.start()
        self.cmd_thread.join()
        self.data_thread.join()

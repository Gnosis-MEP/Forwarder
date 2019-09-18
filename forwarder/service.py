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

    def get_destination_streams(self, destination):
        return self.stream_factory.create(destination, stype='streamOnly')

    def forward_to_subscriber(self, event_data):
        sub_id = f'{event_data["publisher_id"]}-sub'  # this is totally wrong, this is just to have something
        json_msg = event_data_to_json(event_data)
        self.get_destination_streams(sub_id).write_events(json_msg)

    # def get_event_output_for_subscriber(self, event_data):

    def add_query(self, subscriber_id, query_id, publisher_id):
        pass

    def del_query(self, query_id):
        pass

    def process_data(self):
        self.logger.debug('Processing DATA..')
        if not self.service_stream:
            return
        event_list = self.service_stream.read_events(count=1)
        for event_tuple in event_list:
            event_id, json_msg = event_tuple
            event_data = load_event_data(json_msg)
            self.logger.debug(f'Processing new data: {event_data}')
            self.forward_to_subscriber(event_data)

    def process_action(self, action, event_data, json_msg):
        super(Forwarder, self).process_action(action, event_data, json_msg)
        if action == 'addQuery':
            subscriber_id = event_data['subscriber_id']
            query_id = event_data['query_id']
            publisher_id = event_data['publisher_id']
            self.add_query(subscriber_id, query_id, publisher_id)
        elif action == 'delQuery':
            query_id = event_data['query_id']
            self.del_query(query_id)

    def log_state(self):
        super(Forwarder, self).log_state()
        self.logger.info(f'My service name is: {self.name}')

    def run(self):
        super(Forwarder, self).run()
        self.cmd_thread = threading.Thread(target=self.run_forever, args=(self.process_cmd,))
        self.data_thread = threading.Thread(target=self.run_forever, args=(self.process_data,))
        self.cmd_thread.start()
        self.data_thread.start()
        self.cmd_thread.join()
        self.data_thread.join()

import functools
import threading

from event_service_utils.logging.decorators import timer_logger
from event_service_utils.services.event_driven import BaseEventDrivenCMDService
from event_service_utils.tracing.jaeger import init_tracer


class Forwarder(BaseEventDrivenCMDService):
    def __init__(self,
                 service_stream_key, service_cmd_key_list,
                 pub_event_list, service_details,
                 stream_factory,
                 logging_level,
                 tracer_configs):

        tracer = init_tracer(self.__class__.__name__, **tracer_configs)
        super(Forwarder, self).__init__(
            name=self.__class__.__name__,
            service_stream_key=service_stream_key,
            service_cmd_key_list=service_cmd_key_list,
            pub_event_list=pub_event_list,
            service_details=service_details,
            stream_factory=stream_factory,
            logging_level=logging_level,
            tracer=tracer,
        )
        self.cmd_validation_fields = ['id']
        self.data_validation_fields = ['id']
        self.query_id_to_subscriber_id_map = {}

    def get_destination_streams(self, destination):
        return self.stream_factory.create(destination, stype='streamOnly')

    def forward_to_query_ids_stream(self, event_data):
        query_id = event_data.get('query_id')
        self.logger.debug('Sending {event_data} to {query_ids} streams')
        # for event in event_data['vekg_stream']:
        self.write_event_with_trace(event_data, self.get_destination_streams(query_id))

    def forward_to_final_stream(self, event_data):
        self.forward_to_query_ids_stream(event_data)

    def add_query(self, subscriber_id, query_id):
        self.query_id_to_subscriber_id_map[query_id] = subscriber_id

    def del_query(self, query_id):
        self.query_id_to_subscriber_id_map.pop(query_id, None)

    @timer_logger
    def process_data_event(self, event_data, json_msg):
        if not super(Forwarder, self).process_data_event(event_data, json_msg):
            return False
        self.forward_to_final_stream(event_data)

    def process_event_type(self, event_type, event_data, json_msg):
        if not super(Forwarder, self).process_event_type(event_type, event_data, json_msg):
            return False
        if event_type == 'QueryCreated':
            subscriber_id = event_data['subscriber_id']
            query_id = event_data['query_id']
            self.add_query(subscriber_id, query_id)
        elif event_type == 'QueryRemoved':
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

import threading

from event_service_utils.logging.decorators import timer_logger
from event_service_utils.services.tracer import BaseTracerService
from event_service_utils.tracing.jaeger import init_tracer


class Forwarder(BaseTracerService):
    def __init__(self,
                 service_stream_key, service_cmd_key,
                 stream_factory,
                 logging_level,
                 tracer_configs):
        tracer = init_tracer(self.__class__.__name__, **tracer_configs)
        super(Forwarder, self).__init__(
            name=self.__class__.__name__,
            service_stream_key=service_stream_key,
            service_cmd_key=service_cmd_key,
            stream_factory=stream_factory,
            logging_level=logging_level,
            tracer=tracer,
        )
        self.cmd_validation_fields = ['id', 'action']
        self.data_validation_fields = ['id']

        self.query_id_to_subscriber_id_map = {}

    def get_destination_streams(self, destination):
        return self.stream_factory.create(destination, stype='streamOnly')

    def forward_to_query_ids_stream(self, event_data):
        query_ids = event_data.get('query_ids', [])
        self.logger.debug('Sending {event_data} to {query_ids} streams')
        for query_id in query_ids:
            self.write_event_with_trace(event_data, self.get_destination_streams(query_id))

    def forward_to_final_stream(self, event_data):
        self.forward_to_query_ids_stream(event_data)

    def add_query(self, subscriber_id, query_id):
        self.query_id_to_subscriber_id_map[query_id] = subscriber_id

    def del_query(self, query_id):
        self.query_id_to_subscriber_id_map.pop(query_id, None)

    # def send_event_to_somewhere(self, event_data):
    #     self.logger.debug(f'Sending event to somewhere: {event_data}')
    #     self.write_event_with_trace(event_data, self.somewhere_stream)

    @timer_logger
    def process_data_event(self, event_data, json_msg):
        if not super(Forwarder, self).process_data_event(event_data, json_msg):
            return False
        self.forward_to_final_stream(event_data)

    def process_action(self, action, event_data, json_msg):
        if not super(Forwarder, self).process_action(action, event_data, json_msg):
            return False
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

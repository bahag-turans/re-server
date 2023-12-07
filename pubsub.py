from google.cloud import pubsub_v1


class PubSub:
    def __init__(self, project_id="hub-roitraining01-poc-d6aa", topic_name="event-participation", subscription_name="event-participation-sub"):
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.topic_path = self.publisher.topic_path(project_id, topic_name)
        self.subscription_path = self.subscriber.subscription_path(project_id, subscription_name)

    def participate_event(self, userid, eventid):
        message_data = f"User {userid} attends the event {eventid}"
        message_bytes = message_data.encode("utf-8")

        print(f"Publishing message: {message_data}")
        future = self.publisher.publish(self.topic_path, message_bytes)
        return future.result()
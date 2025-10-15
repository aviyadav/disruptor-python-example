from disruptor import Disruptor, BusySpinWaitStrategy
import time
import threading

def event_factory():
    return None  # Placeholder

# Create disruptor with buffer size 1024, 1 producer, 1 consumer
disruptor = Disruptor(event_factory, 1024, 1, 1, BusySpinWaitStrategy())
disruptor.start()

producer = disruptor.get_producer()

# Produce some events
def produce():
    for i in range(10):
        producer.publish_event(f"Event {i}")
        time.sleep(0.1)

threading.Thread(target=produce).start()

# Let it run for a bit
time.sleep(2)
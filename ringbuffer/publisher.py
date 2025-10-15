#!/usr/bin/env python3
import time
from ringbuffer import RingBuffer

def main():
    rb = RingBuffer()
    for i in range(500):
        try:
            msg = f"Message {i+1}"
            rb.put(msg)
            print(f"Published: {msg}")
            time.sleep(1)
        except BufferError as e:
            print(f"Buffer full: {e}")
            time.sleep(0.001)
    rb.close()

if __name__ == "__main__":
    main()

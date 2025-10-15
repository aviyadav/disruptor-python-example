#!/usr/bin/env python3
import time
from ringbuffer import RingBuffer

def main():
    rb = RingBuffer()
    while True:
        try:
            msg = rb.get()
            print(f"Consumed: {msg}")
        except BufferError as e:
            print(f"Buffer empty: {e}")
            time.sleep(0.001)
    rb.close()

if __name__ == "__main__":
    main()

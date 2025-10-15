import os
import json
import fcntl

class RingBuffer:
    def __init__(self, buffer_file='ringbuffer.dat', indices_file='indices.dat', size=10, item_size=256):
        self.buffer_file = buffer_file
        self.indices_file = indices_file
        self.size = size
        self.item_size = item_size
        self.total_size = size * item_size

        # Create buffer file if not exists
        if not os.path.exists(buffer_file):
            with open(buffer_file, 'wb') as f:
                f.write(b'\x00' * self.total_size)

        # Create indices file if not exists
        if not os.path.exists(indices_file):
            with open(indices_file, 'w') as f:
                json.dump({'read_index': 0, 'write_index': 0}, f)

        self.buffer_fd = open(buffer_file, 'r+b')
        self.indices_fd = open(indices_file, 'r+')

    def _load_indices(self):
        self.indices_fd.seek(0)
        return json.load(self.indices_fd)

    def _save_indices(self, indices):
        self.indices_fd.seek(0)
        json.dump(indices, self.indices_fd)
        self.indices_fd.truncate()

    def put(self, item):
        if not isinstance(item, str):
            raise ValueError("Item must be a string")
        data = item.encode('utf-8').ljust(self.item_size, b'\x00')

        fcntl.lockf(self.indices_fd, fcntl.LOCK_EX)
        try:
            indices = self._load_indices()
            next_write = (indices['write_index'] + 1) % self.size
            if next_write == indices['read_index']:
                raise BufferError("Buffer is full")
            pos = indices['write_index'] * self.item_size
            self.buffer_fd.seek(pos)
            self.buffer_fd.write(data)
            indices['write_index'] = next_write
            self._save_indices(indices)
        finally:
            fcntl.lockf(self.indices_fd, fcntl.LOCK_UN)

    def get(self):
        fcntl.lockf(self.indices_fd, fcntl.LOCK_EX)
        try:
            indices = self._load_indices()
            if indices['read_index'] == indices['write_index']:
                raise BufferError("Buffer is empty")
            pos = indices['read_index'] * self.item_size
            self.buffer_fd.seek(pos)
            data = self.buffer_fd.read(self.item_size)
            item = data.rstrip(b'\x00').decode('utf-8')
            indices['read_index'] = (indices['read_index'] + 1) % self.size
            self._save_indices(indices)
            return item
        finally:
            fcntl.lockf(self.indices_fd, fcntl.LOCK_UN)

    def close(self):
        self.buffer_fd.close()
        self.indices_fd.close()
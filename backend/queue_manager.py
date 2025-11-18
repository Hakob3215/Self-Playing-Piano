from collections import deque

class QueueManager:
    def __init__(self):
        self.queue = deque()
        self.current_song = None

    def add_song(self, file_path):
        self.queue.append(file_path)

    def get_next_song(self):
        if self.queue:
            self.current_song = self.queue.popleft()
            return self.current_song
        return None

    def get_queue_list(self):
        return list(self.queue)
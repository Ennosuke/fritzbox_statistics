from watchdog.observers import Observer
from HTMLEventHandler import HTMLEventHandler
import time


class HTMLFileWatcher:
    def __init__(self, src_path):
        self.__src_path=src_path
        self.__event_observer = Observer()
        self.__event_handler = HTMLEventHandler()

    def run(self):
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def start(self):
        self.__schedule()
        self.__event_observer.start()

    def stop(self):
        self.__event_observer.stop()
        self.__event_observer.join()

    def __schedule(self):
        self.__event_observer.schedule(
            self.__event_handler,
            self.__src_path,
            recursive=False
        )


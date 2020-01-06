from watchdog.events import RegexMatchingEventHandler
from HTMLProcessor import HTMLProcessor
import time


class HTMLEventHandler(RegexMatchingEventHandler):
    HTML_REGEX = [r".*\.html$"]

    def __init__(self):
        super().__init__(self.HTML_REGEX)
        self._html_processor = HTMLProcessor(archive_path="D:\\Programmierung\\python\\FBUsageAnalyzer\\archive", csv_file="/data\\test.data")

    def on_created(self, event):
        self.process(event)

    def process(self, event):
        time.sleep(2)
        self._html_processor.process(event.src_path)
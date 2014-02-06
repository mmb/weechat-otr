import subprocess
import time

import watchdog.observers
import watchdog.events

class CodeModifiedEventHandler(watchdog.events.PatternMatchingEventHandler):

    def __init__(self, command):
        super(CodeModifiedEventHandler, self).__init__(['*.py'])
        self.command = command

    def on_any_event(self, event):
        try:
            print(subprocess.check_output(self.command))
        except subprocess.CalledProcessError as err:
            print(err.output)

        print('-' * 80)

class TestWatcher(object):

    def __init__(self, path, command):
        self.observer = watchdog.observers.Observer()
        handler = CodeModifiedEventHandler(command)
        self.observer.schedule(handler, path, recursive=True)

    def start(self):
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

if __name__ == '__main__':
    TestWatcher('.', ['python', '-m', 'unittest', 'discover']).start()

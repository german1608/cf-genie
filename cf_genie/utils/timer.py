import datetime
import time

import cf_genie.logger as logger


class Timer(logger.Loggable):
    """Context handler to measure time of a function"""

    def __init__(self, action_name, log=None):
        super().__init__()
        self.action_name = action_name
        self.log = log or self.log
        self.log.info("Starting: %s", self.action_name)

        self.start_time = time.time()
        self.end_time = None
        self.duration = None

    def __enter__(self):
        return self.start_time

    def __exit__(self, type, value, traceback):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

        self.log.info("Finishing: %s", self.action_name)
        self.log.info("Done in %s seconds.", datetime.timedelta(seconds=self.duration))

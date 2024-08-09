import time
import logging

log = logging.getLogger('bot.' + __name__)


class Timeout:
    def __init__(self):
        # load the shitpost and command call frequencies out of the passed config.
        self.type = dict()
        self.timeout_storage_variable = {}

    def check_timeout(self, timeout_member_name: str, timeout_duration: int, commit=True):
        """Checks timeout variable for specific action.  Returns True if the action is able to proceed and false if the
        action can't"""
        if timeout_member_name not in self.timeout_storage_variable or \
                time.time() > self.timeout_storage_variable[timeout_member_name]:
            if commit:
                self.commit_timeout(timeout_member_name, timeout_duration)
            log.debug("CHECK_TIMEOUT - PASSED request: %s for duration %d" % (timeout_member_name, timeout_duration))
            log.debug("Current check variable: %s" % self.timeout_storage_variable)
            return True
        else:
            log.debug("CHECK_TIMEOUT - FAILED request: %s for duration %d" % (timeout_member_name, timeout_duration))
            return False

    def commit_timeout(self, timeout_member_name: str, timeout_duration: int):
        self.timeout_storage_variable[timeout_member_name] = time.time() + timeout_duration

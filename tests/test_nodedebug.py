import logging
import unittest

from erdpy import nodedebug


class TestNodeDebug(unittest.TestCase):

    def test_start_stop(self):
        pass
        # nodedebug.start()
        # self.assertTrue(nodedebug._is_running())
        # nodedebug.stop()
        # self.assertFalse(nodedebug._is_running())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

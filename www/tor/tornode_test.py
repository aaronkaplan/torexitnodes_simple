import os
import tornode
import unittest
import tempfile

class TornodeTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, tornode.app.config['DATABASE'] = tempfile.mkstemp()
        tornode.app.config['TESTING'] = True
        self.app = tornode.app.test_client()
        tornode.init_db()



    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(tornode.app.config['DATABASE'])



if __name__ == '__main__':
    unittest.main()

#   Copyright (c) 2018 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import parl
import unittest
import time
import threading

from parl.remote.master import Master
from parl.remote.worker import Worker
from parl.remote.client import disconnect
from parl.remote.monitor import ClusterMonitor


@parl.remote_class(max_memory=200)
class Actor(object):
    def __init__(self, x=10):
        self.x = x
        self.data = []

    def add_100mb(self):
        self.data.append(os.urandom(100 * 1024**2))
        self.x += 1
        return self.x


class TestMaxMemory(unittest.TestCase):
    def tearDown(self):
        disconnect()

    def test_max_memory(self):
        port = 3001
        master = Master(port=port)
        th = threading.Thread(target=master.run)
        th.start()
        time.sleep(1)
        worker = Worker('localhost:{}'.format(port), 1)
        cluster_monitor = ClusterMonitor('localhost:{}'.format(port))
        time.sleep(1)
        parl.connect('localhost:{}'.format(port))
        actor = Actor()
        time.sleep(30)
        self.assertEqual(1, cluster_monitor.data['clients'][0]['actor_num'])
        actor.add_100mb()
        time.sleep(50)
        self.assertEqual(0, cluster_monitor.data['clients'][0]['actor_num'])
        actor.job_socket.close(0)
        del actor
        worker.exit()
        master.exit()


if __name__ == '__main__':
    unittest.main()

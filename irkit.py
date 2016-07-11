#!/usr/bin/python
# encoding: utf-8

import sys
import os
import json
import subprocess

from workflow import Workflow
from workflow import web

ALFRED_CONFIG_JSON_PATH = os.path.join(os.environ['HOME'], '.irkit.json')


class Client(object):
    IRKIT_API_ENDPOINT = 'https://api.getirkit.com/1/messages'

    def __init__(self, config, device_name=None):
        self.config = config
        devices = config['Device']
        if not device_name:
            device_name = devices.keys()[0]
        self.device = devices[device_name]

    def post_signal(self, name):
        ir = self.config['IR'][name]
        message = json.dumps(ir)
        params = {
            'clientkey': self.device['clientkey'],
            'deviceid': self.device['deviceid'],
            'message': message
        }
        web.post(self.IRKIT_API_ENDPOINT, data=params)

def main_search(wf): 
    args = wf.args
    query = args[0]
    with open(ALFRED_CONFIG_JSON_PATH, 'r') as f:
        config = json.loads(f.read())
        devices = config['Device']
        device = devices.keys()[0]
        irs = config['IR']
        names = wf.filter(query, irs.keys())
        for name in names:
            wf.add_item("Post %s" % name, "via %s" % device,
                        arg=name,
                        valid=True)
    wf.send_feedback()

def main_post(wf):
    with open(ALFRED_CONFIG_JSON_PATH, 'r') as f:
        config = json.loads(f.read())
        client = Client(config)
        name = wf.args[1]
        client.post_signal(name)
        wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow(update_settings={
        'github_slug': 'giginet/alfred-irkit-workflow',
        'version': open(os.path.join(os.path.dirname(__file__), 'version')).read(),
    })
    args = wf.args
    if len(args) >= 2 and args[0] == '--post':
        sys.exit(wf.run(main_post))
    sys.exit(wf.run(main_search))

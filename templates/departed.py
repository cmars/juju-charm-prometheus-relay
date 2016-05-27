#!/usr/bin/env python3

import os
import sys
from subprocess import check_call

sys.path.append('lib')

from charmhelpers.core import hookenv


if __name__ == '__main__':
    env = {}
    env.update(os.environ)
    env['ETCDCTL_ENDPOINT'] = hookenv.config().get('etcd')
    try:
        check_call(['etcdctl', 'rm', '/{{ relay_name }}/{{ role }}'], env=env)
    except Exception as e:
        hookenv.log("error removing remote relation data: %s" % (e))

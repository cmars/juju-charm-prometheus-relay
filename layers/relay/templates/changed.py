#!/usr/bin/env python3

import json
import os
import sys
from subprocess import check_call

sys.path.append('lib')

from charmhelpers.core import hookenv, unitdata


if __name__ == '__main__':
    relname = hookenv.relation_type()
    role, _ = hookenv.relation_to_role_and_interface(relname)

    local_data = hookenv.relation_get()
    env = {}
    env.update(os.environ)
    env['ETCDCTL_ENDPOINT'] = hookenv.config().get('etcd')
    check_call(['etcdctl', 'set', '/{{ relay_name }}/{{ counterpart }}', json.dumps(local_data)], env=env)

    kv = unitdata.kv()
    kv.set('relay.local.relation.name', relname)
    kv.set('relay.local.relation.role', role)
    kv.set('relay.remote.relation.role', '{{ counterpart }}')
    kv.flush(save=True)

    # Invoke update-status immediately to trigger polling etcd
    os.execl(os.path.join(hookenv.charm_dir(), 'hooks/update-status'), 'update-status')

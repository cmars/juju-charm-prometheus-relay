# layer-relay

This layer is used to build "relay" charms that can be used to establish a relation across Juju models.

# Usage

For a given relation type, create a reactive layered charm that includes this
layer like this:

    includes:
      - layer:relay

and annotates the relation endpoints you'd like to relay across models with
`relay: <relay-name>`, where _relay-name_ is a unique relay name for your
multi-model deployment.

## Example

We can relay any kind of relation, but for this example, we'll relay http. Add
this layer as shown above, then create a `metadata.yaml`:

    name: myapp-relay
    summary: cross-model relay for myapp
    description: cross-model relay for myapp
    provides:
      frontend:
        interface: http
        relay: myapp
    requires:
      backend:
        interface: http
        relay: myapp

Deploy the charm on xenial, and then you can set up a cross-model relay:

    juju deploy -m M1 ~/charms/myapp-relay --series xenial
    juju set-config -m M1 myapp-relay etcd=10.0.0.1:4001,10.0.0.2:4001,10.0.0.3:4001
    juju add-relation -m M1 myapp-relay:frontend myapp  # relay acts like a "frontend" here

    juju deploy -m M2 ~/charms/myapp-relay --series xenial
    juju set-config -m M2 myapp-relay etcd=10.0.0.1:4001,10.0.0.2:4001,10.0.0.3:4001
    juju add-relation -m M2 myapp-relay:backend nginx   # relay acts like a "backend" here

What just happened? Well, we:

- Deployed a myapp-relay into each model, M1 and M2
- Configured both to relay relations through the same etcd cluster
- Connected a backend, myapp, to the relay in M1 where it acts like a "frontend"
- Connected the relay, acting like the "backend" in M2, to a frontend, nginx.

The relation data between myapp and nginx are relayed to each other through
changes in etcd, which is polled by the relay.

The relay charm itself is quite small, just a `layer.yaml` and `metadata.yaml`,
so it's easy to make one for each logical cross-model relation boundary in your
multi-model deployment. Just give each one a distinct relay name.

# Requirements

Charms built with this layer only support xenial, as there are no earlier
backports of etcdctl in the archives.

The etcd cluster must be network accessible from the workloads in both models.

The network addresses that each workload sets on its relation needs to be reachable from
the counterpart workload on the other side of the relay.

# Caveats

This layer does not ensure confidentiality of network traffic over public
networks. The relayed charms are responsible for TLS and other necessary
security measures.

Relayed relations may take longer to propagate than normal relations, since the
relay is polling etcd. To move things along, you can cause a relay to poll
immediately with `juju run --service some-relay 'hooks/update-status'`.

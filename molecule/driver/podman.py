#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#  Copyright (c) 2019 Satoru SATOH <satoru.satoh@gmail.com>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

from __future__ import absolute_import

import os

from molecule import logger
from molecule.driver import docker

LOG = logger.get_logger(__name__)


class Podman(docker.Docker):
    """
    The class responsible for managing containers controlled by `Podman`_ .
    `Podman`_ is `not` the default driver used in Molecule.

    .. code-block:: yaml

        driver:
          name: podman
        platforms:
          - name: instance
            hostname: instance
            image: image_name:tag
            dockerfile: Dockerfile.j2
            pull: True|False
            pre_build_image: True|False
            registry:
              url: registry.example.com
              credentials:
                username: $USERNAME
                password: $PASSWORD
                email: user@example.com
            override_command: True|False
            command: sleep infinity
            pid_mode: host
            privileged: True|False
            security_opts:
              - seccomp=unconfined
            volumes:
              - /sys/fs/cgroup:/sys/fs/cgroup:ro
            tmpfs:
              - /tmp
              - /run
            capabilities:
              - SYS_ADMIN
            exposed_ports:
              - 53/udp
              - 53/tcp
            published_ports:
              - 0.0.0.0:8053:53/udp
              - 0.0.0.0:8053:53/tcp
            ulimits:
              - nofile:262144:262144
            dns_servers:
              - 8.8.8.8
            networks:
              - name: foo
              - name: bar
            docker_host: tcp://localhost:12376
            env:
            buildargs:
                http_proxy: http://proxy.example.com:8080/

    If specifying the `CMD`_ directive in your ``Dockerfile.j2`` or consuming a
    built image which declares a ``CMD`` directive, then you must set
    ``override_command: False``. Otherwise, Molecule takes care to honour the
    value of the ``command`` key or uses the default of ``bash -c "while true;
    do sleep 10000; done"`` to run the container until it is provisioned.

    When attempting to utilize a container image with `systemd`_ as your init
    system inside the container to simulate a real machine, make sure to set
    the ``privileged``, ``volume_mounts``, ``command``, and ``environment``
    values. An example using the ``centos:7`` image is below:

    .. note:: Do note that running containers in privileged mode is considerably
              less secure. For details, please reference `Docker Security
              Configuration`_

    .. code-block:: yaml

        platforms:
        - name: instance
          image: centos:7
          privileged: true
          volume_mounts:
            - "/sys/fs/cgroup:/sys/fs/cgroup:rw"
          command: "/usr/sbin/init"
          environment:
            container: docker

    .. code-block:: bash

        $ pip install molecule[docker]

    When pulling from a private registry, the username and password must be
    exported as environment variables in the current shell. The only supported
    variables are $USERNAME and $PASSWORD.

    .. code-block:: bash

        $ export USERNAME=foo
        $ export PASSWORD=bar

    Provide the files Molecule will preserve upon each subcommand execution.

    .. code-block:: yaml

        driver:
          name: podman
          safe_files:
            - foo

    .. _`Podman`: https://podman.io
    .. _`systemd`: https://www.freedesktop.org/wiki/Software/systemd/
    .. _`CMD`: https://docs.docker.com/engine/reference/builder/#cmd
    """  # noqa

    def __init__(self, config):
        super(Podman, self).__init__(config)
        self._name = 'podman'

    def login_cmd_template(self):
        return ('podman exec '
                '-e COLUMNS={columns} '
                '-e LINES={lines} '
                '-e TERM=bash '
                '-e TERM=xterm '
                '-ti {instance} bash')

    def login_options(self, instance_name):
        return {'instance': instance_name}

    def ansible_connection_options(self, instance_name):
        """
        .. todo::
           I'm waiting for the version contains this:
           https://github.com/ansible/ansible/pull/47519
        """
        return {}

Opwen cloudserver
=================

.. image:: https://travis-ci.org/OPWEN/opwen-cloudserver.svg?branch=master
  :target: https://travis-ci.org/OPWEN/opwen-cloudserver

What's this?
------------

This repository contains the source code for the Opwen cloud server. Its purpose
is to connect the `application <https://github.com/OPWEN/opwen-webapp>`_ running
on the Opwen Lokole devices to the rest of the world.

The server has two main responsibilities:

1. Receive emails from the internet that are addressed to Lokole users and
   forward them to the appropriate Lokole device.
2. Send new emails created by Lokole users to the rest of the internet.

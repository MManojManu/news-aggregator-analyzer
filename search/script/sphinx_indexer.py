from __future__ import unicode_literals
import os

"""Indexer file"""
class Process(object):

    def start(self):
        sudoPassword = ''
        command = 'sudo indexer --config /etc/sphinxsearch/sphinx.conf --all --rotate'
        os.system('echo %s|sudo -S %s' % (sudoPassword, command))

obj_process = Process()
obj_process.start()

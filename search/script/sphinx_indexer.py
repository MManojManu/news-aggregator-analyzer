from __future__ import unicode_literals
from __future__ import print_function
import os

"""Indexer file"""
class Process(object):

    def start(self):
        sudoPassword = 'codephanther'
	command = 'sudo service sphinxsearch stop'
	os.system('echo %s|sudo -S %s' % (sudoPassword, command))
	print('\nStopped the Server')
	command = 'sudo /var/lib/sphinxsearch/data/*'
	os.system('echo %s|sudo -S %s' % (sudoPassword, command))
	print("Deleted the old Index files")
        command = 'sudo indexer --config /etc/sphinxsearch/sphinx.conf --all'
        os.system('echo %s|sudo -S %s' % (sudoPassword, command))
	command = 'sudo service sphinxsearch start'
	os.system('echo %s|sudo -S %s' % (sudoPassword, command))
	print('\nStarted the Server')

obj_process = Process()
obj_process.start()


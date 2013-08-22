#! /usr/bin/python

import cgi
from wsgiref.simple_server import make_server
from bomb import Batch

def application(envrion, start_response):
	config, cfile = envrion['QUERY_STRING'].split('|')
	batch = Batch(config)

	if cfile.endswith('.css'):
		start_response('200 OK', [('Content-Type', 'text/stylesheet')])
	else:
		start_response('200 OK', [('Content-Type', 'text/plain')])

	return batch.group.dump(cfile)


if __name__ == '__main__':
	httpd = make_server('', 8866, application)
	httpd.serve_forever()
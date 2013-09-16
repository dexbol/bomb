#! /usr/bin/python

import cgi
import argparse
from wsgiref.simple_server import make_server
from bomb import Batch

def application(envrion, start_response):
	config, cfile = envrion['QUERY_STRING'].split('|')
	batch = Batch(config)

	if cfile.endswith('.css'):
		start_response('200 OK', [('Content-Type', 'text/css')])
	else:
		start_response('200 OK', [('Content-Type', 'text/plain')])

	return batch.group.dump(cfile)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('host', nargs="?")
	args = parser.parse_args();
	host = vars(args)['host'] or ''
	httpd = make_server('', 8866, application)
	print 'Serving on port 8866 ...'
	httpd.serve_forever()
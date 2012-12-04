import os
import sys
import re
import logging
import argparse


HOST_PATH = r'C:\Windows\System32\drivers\etc\hosts'

DEV_HOST = {
	'source.dev.v.6.cn': '127.0.0.1'
}

NORMAL_HOST = {
	'source.dev.v.6.cn': '122.70.141.41'	
}


def switch():
	arg_parse = argparse.ArgumentParser()
	arg_parse.add_argument('--dev', action='store_true', help='develope host')
	arg_parse.add_argument('--normal', action='store_true')
	args = vars(arg_parse.parse_args())
	handler = open(HOST_PATH)
	lines = handler.readlines()
	handler.close()
	result = []
	if args['dev']:
		host = DEV_HOST
	else:
		host = NORMAL_HOST
	for line in lines:
		for domain in host:
			if line.find(domain) > -1:
				result.append(host[domain] + ' ' + domain + '\n')
			else:
				result.append(line)
	handler = open(HOST_PATH, 'w')
	handler.write(''.join(result))


if __name__ == '__main__':
	switch()

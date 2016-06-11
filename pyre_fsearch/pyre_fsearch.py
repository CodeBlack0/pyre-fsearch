#!/usr/bin/python
import argparse
import os
from queue import Queue
import re
from stat import *
import sys
import threading
import time

def path_r2a(path):
	return os.path.join(os.getcwd(), path)

def search_file(path, expression, re_options=re.I|re.M):
	results = []
	with open(path) as f:
		for i, line in enumerate(f):
			if re.search(expression, line, re_options):
				results.append((i,line))
	return results

def walktree(top, filelist=[]):
    '''recursively descend the directory tree rooted at top,
       calling the callback function for each regular file'''

    for f in os.listdir(top):
        pathname = os.path.join(top, f)
        mode = os.stat(pathname)[ST_MODE]
        if S_ISDIR(mode):
            # It's a directory, recurse into it
            walktree(pathname, filelist)
        elif S_ISREG(mode):
            # It's a file, call the callback function
            if pathname.endswith('.py') or pathname.endswith('.txt') or pathname.endswith('.c') or pathname.endswith('.cpp') or pathname.endswith('.h') or pathname.endswith('.hpp') or pathname.endswith('.rb'):
            	filelist.append(pathname)

def search_files_threaded(files, expression, re_options, number_of_threads=1):
	queue = Queue()
	lock = threading.Lock()
	threadlist = []
	results = {}

	def worker():
		while True:
			path = queue.get()
			result = search_file(path, expression, re_options)
			with lock:
				results[path] = result
			queue.task_done()

	for i in range(number_of_threads):
		thread = threading.Thread(target=worker)
		thread.daemon = True
		threadlist.append(thread)

	for path in files:
		queue.put(path)

	start = time.perf_counter()
	for thread in threadlist:
		thread.start()
	queue.join()
	time_taken = time.perf_counter() - start

	return results, time_taken

def Main():
	parser = argparse.ArgumentParser(description='Search given path for a given Regular Expression')
	parser.add_argument('paths', type=str, nargs='+', help='path to search at')
	parser.add_argument('-e', '--expression', required=True, nargs='?', const='', default='', help='regular expression to search by')
	volume_group = parser.add_mutually_exclusive_group()
	volume_group.add_argument('-v', '--verbose', help='verbose output', action='store_true')
	volume_group.add_argument('-q', '--quiet', help='quiet output', action='store_true')
	parser.add_argument('-o', '--output', nargs='?', const=os.path.join(os.getcwd(), 're_search_results.txt'), default='', help='output results to a file')
	parser.add_argument('-t', '--threads', nargs='?', const='-1', default='1', help='enable multithreading')

	args = parser.parse_args()

	filelist = []
	for path in args.paths:		
		if not os.path.isabs(path):
			path = path_r2a(path)
		if os.path.isdir(path):
			walktree(path, filelist)
		elif os.path.isfile(path):
			filelist.append(path)

	re_options = re.I|re.M
	number_of_threads = args.threads == '-1' and len(filelist) or int(args.threads)
	results, time_taken = search_files_threaded(filelist, args.expression, re_options, number_of_threads)

	if args.verbose:
		print('Regular Expression: "{0}"'.format(args.expression))
		print('Search Path/s: {0}'.format(','.join([(os.path.isabs(path) and path or path_r2a(path)) for path in args.paths])))
		print('-'*75)
		for file in results:
			if len(results[file]) > 0:
				print(file+'\n'+'\n'.join(['line {0:4d}: "{1}"'.format(int(x[0]), x[1].strip()) for x in results[file]])+'\n')
		print('-'*75)
		print('Time taken: {0:2.10f}'.format(time_taken))

	if args.quiet:
		print('Regular Expression: "{0}"'.format(args.expression))
		print('Search Path/s: {0}'.format(','.join([(os.path.isabs(path) and path or path_r2a(path)) for path in args.paths])))
		for file in results:
			if len(results[file]) > 0:
				print(file+'\nline/s: '+','.join(['{0:4d}'.format(x[0]) for x in results[file]]))
		print('Time taken: {0:2.10f}'.format(time_taken))

	if args.output:
		with open(args.output, 'a') as of:
			of.write('Regular Expression: "{0}"\n'.format(args.expression))
			of.write('Search Path/s: {0}\n'.format(','.join([(os.path.isabs(path) and path or path_r2a(path)) for path in args.paths])))
			of.write('Number of threads: {0}\n'.format(number_of_threads))
			of.write('-'*75)
			for file in results:
				if len(results[file]) > 0:
					of.write('\n'+file+'\n'+'\n'.join(['line {0:4d}: "{1}"'.format(int(x[0]), x[1].strip()) for x in results[file]])+'\n')
			of.write('-'*75+'\n')
			of.write('Time taken: {0:2.10f}\n\n'.format(time_taken))

if __name__ == '__main__':
	Main()
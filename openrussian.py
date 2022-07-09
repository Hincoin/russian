import requests
import sys
import os
import unicodedata
from multiprocessing.pool import ThreadPool
import concurrent.futures
import json
import ast
import pprint
import csv
import argparse



def strip_accent(line):
	# ' is used for emphasis from api.openrussian.org, 
	# but the site doesn't index words with the accent markers. 
	bare = line.replace("'", "")
	return bare

def generate_api_request_for_word(word):
	return "https://api.openrussian.org/suggestions?q={}&lang=en".format(word)

def generate_api_request_for_csv_entry(entry):
	#russian,english
	print("Entry = {}".format(entry))
	russian, english = entry.split(',', 1)

	# There may be a number of russian words, since some CSV entries 
	# are phrases.
	russian_words = russian.split(' ')

	# Craft a request for each one
	http_requests = tuple(
		generate_api_request_for_word(word) for word in russian_words
	)
	return (entry, http_requests)

def make_word_request(word):
	return requests.get(word)

def make_csv_request(entry_pair):
	entry, raw_reqs = entry_pair
	reqs = tuple(
		requests.get(raw_req) for raw_req in raw_reqs
	)
	return (entry, reqs)

def verify_link(link):
	return (link, requests.get(link[1:-1]).status_code)
def verify_links(links):
	with concurrent.futures.ThreadPoolExecutor() as executor:
		results = executor.map(verify_link, links)
		for r in results:
			link, code = r
			print("Got result for {} -- {}".format(link, code))
			if code != 200:
				print("***** {} has code {}".format(link, code))

def make_link_from_request(req):
	js = req.json()
	if 'result' not in js:
		return []
	result = js['result']
	if 'words' not in result:
		return []

	words = js['result']["words"]
	if not words:
		return []

	word = words[0]
	ru = word['ru']
	ru = strip_accent(ru)
	return "https://en.openrussian.org/ru/{}".format(ru)


def russify_csv(csv_file):
	with open(csv_file, 'r') as f:
		lines = f.readlines()[1:]
		csv_entry_requests = [generate_api_request_for_csv_entry(line) for line in lines]
		new_file_contents = []
		with concurrent.futures.ThreadPoolExecutor() as executor:

			results = executor.map(make_csv_request, csv_entry_requests)
			for result in results:
				entry, res = result
				links = []
				for r in res:
					link = make_link_from_request(r)
					links.append("'{}'".format(link))
					# # js = json.loads(r.json())
					# # d = ast.literal_eval(js)
					# js = r.json()
					# if 'result' not in js:
					# 	continue
					# if 'words' in js['result']:
					# 	words = js['result']["words"]
					# 	if words:
					# 		word = words[0]
					# 		ru = word['ru']
					# 		ru = strip_accent(ru)
					# 		links.append("'https://en.openrussian.org/ru/{}'".format(ru))
					# else:
					# 	pass#print("no words for {}".format(entry))
					# #print("Got: {}".format(r.json()))

				#verify_links(links)
				#print("Got links for {}".format(entry))
				row = entry.replace('\n','').split(',', 1)
				row.extend(links)
				new_file_contents.append(row)


		new_file_name = csv_file.replace(".csv", "") + "_links.csv"
		with open(new_file_name, 'w') as new_file:
			writer = csv.writer(new_file)
			for new_line in new_file_contents:
				writer.writerow(new_line)

		print("Done writing to {}".format(new_file_name))

def russify_words(words):
	word_requests = [
		generate_api_request_for_word(word) for word in words
	]

	with concurrent.futures.ThreadPoolExecutor() as executor:
		results = executor.map(make_word_request, word_requests)
		for result in results:
			link = make_link_from_request(result)
			print("{}".format(link))



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Generate openrussian.org links")
	parser.add_argument('--word', '-w', action='append')
	parser.add_argument('--file', '-f')

	args = parser.parse_args()
	if args.file:
		russify_csv(args.file)
	elif args.word:
		russify_words(args.word)
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
	# Create the URL that we need to fetch from requests lib
	# for a given word.
	return "https://api.openrussian.org/suggestions?q={}&lang=en".format(word)

def generate_api_request_for_csv_entry(entry):
	#russian,english
	print("Entry = {}".format(entry))

	# Sometimes the english portion has commas.
	# We only want to split on the first comma since this
	# is a CSV file. 
	russian, english = entry.split(',', 1)

	# There may be a number of russian words, since some CSV entries 
	# are phrases.
	russian_words = russian.split(' ')

	# Craft a request for each one
	http_requests = tuple(
		generate_api_request_for_word(word) for word in russian_words
	)

	# Make a tuple consisting of the original entry (for-rewriting)
	# and the requests (to execute)
	return (entry, http_requests)

def make_word_request(word):
	return requests.get(word)

def make_csv_request(entry_pair):
	# Execute the actual HTTP request. 
	entry, raw_reqs = entry_pair
	reqs = tuple(
		requests.get(raw_req) for raw_req in raw_reqs
	)
	return (entry, reqs)

# Helper functions to verify that the generated link is valid. 
# Callsite is currently commented out since it takes far too long.
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


def resolve_json_form_of(formOf):
	form = formOf[0]
	source = form.get("source")
	if not source:
		return []

	ru = source['ru']
	ru = strip_accent(ru)
	return "https://en.openrussian.org/ru/{}".format(ru)

def resolve_json_words(words):
	word = words[0]
	ru = word['ru']
	ru = strip_accent(ru)
	return "https://en.openrussian.org/ru/{}".format(ru)

# Parse the JSON result of the request and
# make a link to openrussian.org
def make_link_from_request(req):
	# Each JSON response should have a 'result' key if it
	# is present in the API.
	js = req.json()
	result = js.get('result')
	if not result:
		return []

	# Within the 'result' dictionary, we'll evaluate which of the sub-keys
	# to pick from. 

	# Sometimes we'll have a 'formOf' subkey, which is typically
	# best for resolving other forms of words -- e.g. past tense, cases, masculine/feminine/neut/plural. 
	formOf = result.get('formOf')
	words = result.get('words')
	if not formOf and not words:
		# Neither one matched
		return []
	elif formOf:
		# formOf should be preferred if it has an entry
		return resolve_json_form_of(formOf)
	else:
		return resolve_json_words(words)


def russify_csv(csv_file):
	with open(csv_file, 'r') as f:
		lines = f.readlines()[1:] # First line is a header
		csv_entry_requests = [generate_api_request_for_csv_entry(line) for line in lines]
		new_file_contents = []
		with concurrent.futures.ThreadPoolExecutor() as executor:

			results = executor.map(make_csv_request, csv_entry_requests)
			for result in results:
				entry, res = result
				links = []
				for r in res:
					link = make_link_from_request(r)
					if link:
						links.append("'{}'".format(link))

				#verify_links(links)
				row = entry.replace('\n','').split(',', 1)
				row.extend(links)
				new_file_contents.append(row)


		new_file_name = csv_file.replace(".csv", "") + "_links.csv"
		with open(new_file_name, 'w') as new_file:
			writer = csv.writer(new_file)
			for new_line in new_file_contents:
				writer.writerow(new_line)

		print("Done writing to {}".format(new_file_name))


def russify_words_impl(words):
	word_requests = [
		generate_api_request_for_word(word) for word in words
	]

	russian_words = []
	with concurrent.futures.ThreadPoolExecutor() as executor:
		results = executor.map(make_word_request, word_requests)
		for index, result in enumerate(results):
			og_word = words[index]
			link = make_link_from_request(result)
			russian_words.append((link, og_word))

	return russian_words
def russify_words(words):

	results = russify_words_impl(words)
	for link, og_word in results:
		if link:
			print("{}".format(link))
		else:
			print("No entry found for '{}' :(".format(og_word))


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Generate openrussian.org links")
	parser.add_argument('--word', '-w', action='append')
	parser.add_argument('--file', '-f')

	args = parser.parse_args()
	if args.file:
		russify_csv(args.file)
	elif args.word:
		russify_words(args.word)
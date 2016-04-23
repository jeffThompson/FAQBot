# -*- coding: utf-8 -*-

import wikipedia, re, os, glob, twitter
from collections import Counter
from pattern.en import pluralize, singularize, tag
from random import choice, random, shuffle
from ftplib import FTP
from settings import ftp_settings, twitter_settings
from functions import *


random_article = 	  False			# random article, or random noun?
select_best_article = True			# select first search result
randomize_order = 	  True			# randomize order of Qs?
test_countable = 	  True			# pings Google NGram

max_tries = 		  5				# total # of tries before bailing

testing = 			  False			# run testing mode?
test_thing = 		  'death'		# preset thing to test with


def run():

	# load a list of previous FAQs
	print 'loading previous FAQs...'
	previous_articles = glob.glob('faqs/*.html')
	for i, a in enumerate(previous_articles):
		a = a.replace('.html', '').lower()
		previous_articles[i] = a.replace('faqs/', '')

	# get a list of random articles or random noun
	if random_article:
		print 'getting a list of random articles...'
		all_articles = wikipedia.random(pages=10)
		all_articles = [ a for a in all_articles if not a.startswith('List of ') and not a.endswith('(disambiguation)') and not a.startswith('Comparison of ') ]
		articles = []
		for article in all_articles:
			if article.lower() not in previous_articles:
				articles.append(article)
		print '- found ' + str(len(articles)) + ' new articles'
		thing = choice(articles)
	else:
		print 'selecting random noun...'
		with open('../WordLists/SingularNouns.txt') as f:
			singular_nouns = f.readlines()
		thing = choice(singular_nouns)
	thing = thing.strip()

	# for test version, use 'pronoun' as article
	if testing:
		thing = test_thing

	# find matching articles
	print 'searching Wikipedia for "' + thing + '"...'
	all_articles = wikipedia.search(thing)
	articles = [ a for a in all_articles if not a.startswith('List of ') and not a.endswith('(disambiguation)') ]
	print 'selecting random article...'
	if select_best_article and not random_article:
		try:
			article = wikipedia.page(articles[0])
		
		# catch disambiguation error, select from choices
		except wikipedia.exceptions.DisambiguationError as choices:
			print '- requires disambiguation...'
			choices = str(choices).split('\n')[1:]
			article = wikipedia.page(choices[0])
	else:
		article = wikipedia.page(choice(articles))
	print '- ' + article.title

	# title of article 
	print 'extracting title...'
	thing = article.title
	thing = re.sub(r'\([^)]*\)', '', thing)			# strip ()
	thing = thing.lower()
	print '- ' + thing

	# clean up article content for search
	# unicode should work fine, so no need to replace those chars
	print 'getting article...'
	content = article.content
	content = re.sub(r'\([^)]*\)', ' ', content)	# nothing in ()

	# get POS for thing
	# search in entire article, since context is required
	# for good POS tagging; get most likely POS
	print 'tagging article and getting POS for thing...'
	try:
		tokenized = tag(content)
		pos_list = [ p for w, p in tokenized if w.lower() == thing ]	# get all POS instances for thing
		pos = Counter(pos_list).most_common()[0][0]						# most freq POS in the list = most likely
		pos = re.sub(r'-.*?$', '', pos)									# get rid of relation tags
		print '- ' + pos

		print 'should the thing get a/an in front?'
		no_a_parts = [ 'NNP', 'NNPS' ]
		if pos in no_a_parts:
			print '- no'
			proper_or_verb = True
		else:
			print '- yes'
			proper_or_verb = False
	except:
		print '- no POS info found, assuming non-verb/proper noun'
		proper_or_verb = False

	# search for known things
	print 'gathering mentions of the thing...'
	orig = thing
	plural = pluralize(thing)
	singular = singularize(thing)
	known_things = []
	matches = re.findall('(' + orig + '|' + plural + '|' + singular + ')' + ' (is|are|were|was)(.*?\w{2,})\.', content, re.IGNORECASE)

	# find anything?
	if len(matches) == 0:
		print '- found nothing about this thing'
		print '- quitting... :('
		return False
	print '- found ' + str(len(matches)) + ' items!'

	# should we capitalize?
	print 'should thing be capitalized?'
	upper_count = 0
	lower_count = 0
	for m in matches:
		if m[0][0].isupper():
			upper_count += 1
		else:
			lower_count += 1
	if upper_count > lower_count:
		capitalize = True
		print '- yes!'
	else:
		capitalize = False
		print '- no!'

	# is the thing countable
	# ie: should we use is/are/was/were?
	print 'is the thing countable?'
	if test_countable:
		try:
			countable = countable_noun(thing)
			if countable:
				print '- yes, adding a/an/was/were'
			else:
				print '- nope, no connecting word'
		except:
			print '- error testing, assuming yes...'
			countable = True
	else:
		print '- not running test, assuming yes...'
		countable = True

	# format questions and answers!
	print 'generating questions and answers...'
	items = []
	for m in matches:
		t = m[0].strip()
		conn = m[1].strip()
		k = m[2].strip()

		# convert "it is" to "is it", "they are" to "are they"
		k = re.sub('\bit is\b', 'is it', k)
		k = re.sub('\bhe is\b', 'is he', k)
		k = re.sub('\bshe is\b', 'is she', k)
		k = re.sub('\bthey are\b', 'are they', k)

		# no blank info
		if len(k) == 0 or k[0] in '.,?!':
			continue

		# split into two pieces if possible
		# prioritize split at terminal points; if none, comma
		other = ''
		parts = re.split('(\. |\? |! |; )', k)
		if len(parts) > 1:
			k = parts[0] + parts[1].strip()
			if k[-1] in '.!?;':
				k = k[:-1]

			for part in parts[2:]:
				part = part.strip()
				other += part
				if part == '.' or part == '!' or part == '?' or part == ';':
					other += ' '
		elif ',' in k:
			index = k.find(', ')
			other = k[index+2:]
			if not re.match('(though |although |and |as )', other):
				other = 'and ' + other
			k = k[:index]
		else:
			other = None

		# set a/and/was/were for the word
		if singularize(t) == t:
			are_is = 'Is '
			if conn.lower() == 'was':
				are_is = 'Was '
			
			if not proper_or_verb and countable:
				if t[0] in 'aeiou':
					are_is += 'an '
				else:
					are_is += 'a '
		else:
			are_is = 'Are '
			if conn.lower() == 'were':
				are_is = 'Were '

		# format question and answer
		if capitalize:
			t = t.title()
		else:
			t = t.lower()
		question = are_is + t + ' ' + k
		
		answer = ''
		if other != None:
			answer += 'Yes, ' + other
		else:
			answer += 'Yes'

		# clean up missing quotation marks, parentheses
		if question.count('"') % 2 != 0:
			question += '"'
		if question.count('(') != question.count(')'):
			question += ')'
		if answer.count('"') % 2 != 0:
			answer += '"'
		if answer.count('(') != answer.count(')'):
			answer += ')'

		# final strip pre punctuation
		question = question.strip()
		answer = answer.strip()

		# add to list of items
		items.append({'question': question + '?', 'answer': answer + '.' })

	# randomize order of FAQs
	# (helps not read like the article)
	# keeps first item so it start nice, though :)
	if randomize_order:
		first = [ items[0] ]
		rest = items[1:]
		shuffle(rest)
		items = first + rest

	# create html filename
	html_file = thing
	if html_file == 'index':		# don't save over index.php!
		html_file = 'index_'
	if capitalize:
		html_file = html_file.title()
	html_file = html_file.replace(' ', '_')
	html_file += '.html'

	# format HTML
	print 'formatting HTML file...'
	html = '''<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
		<title>''' + thing.title() + ''' FAQs</title>
		<link href='https://fonts.googleapis.com/css?family=Crimson+Text:400,700' rel='stylesheet' type='text/css'>
		<link href="include/stylesheet.css" rel="stylesheet" type="text/css">
	</head>

	<body>
		<div id="wrapper">
	'''
	html += '		<p id="homeLink"><a href="index.php">&larr;</a></p>\n'
	html += '		<h1>' + thing.title() + ' FAQs:' + '</h1>\n'
	html += '		<hr />\n\n'
	for i, item in enumerate(items):
		html += '		<p class="question" id="q' + str(i) + '"><strong>Q: </strong>' + item['question'] + '<span><a href="' + html_file + '#q' + str(i) + '"> &para;</a></span></p>\n'
		html += '		<p class="answer"><strong>A: </strong>' + item['answer'] + '</p>\n\n'
	html += '''
			<hr />
			<footer>
				<ul>
					<li>More FAQs <a href="https://twitter.com/faqgenerator">@FAQGenerator</a></li>
					<li>A project by <a href="http://www.jeffreythompson.org">Jeff Thompson</a></li>
				</ul>
			</footer>
		</div> <!-- end wrapper -->

		<!-- nice smart quotes, via: http://smartquotesjs.com -->
		<script src="include/smartquotes.min.js"></script>
	</body>
	</html>'''

	# save html to file and upload to server
	with open(html_file, 'w') as f:
		f.write(html.encode('utf8'))

	print 'uploading to server...'
	ftp_address = ftp_settings['ftp_address']
	username = ftp_settings['username']
	password = ftp_settings['password']
	directory = ftp_settings['directory']
	ftp = FTP(ftp_address)
	ftp.login(username, password)
	ftp.cwd(directory)
	ftp.storlines('STOR ' + html_file, open(html_file))
	ftp.quit()
	os.rename(html_file, 'faqs/' + html_file)
	print '- done!'

	# post new FAQ to Twitter
	print 'posting to Twitter...'
	tweet = thing.title() + ' FAQs: http://www.jeffreythompson.org/FAQGenerator/' + html_file

	consumer_key = twitter_settings['consumer_key']
	consumer_secret = twitter_settings['consumer_secret']
	access_token_key = twitter_settings['access_token']
	access_token_secret = twitter_settings['access_token_secret']
	try:
		api = twitter.Api(consumer_key = consumer_key, consumer_secret = consumer_secret, access_token_key = access_token_key, access_token_secret = access_token_secret)
		status = api.PostUpdate(tweet)
		print '  post successful!'
	except twitter.TwitterError:
		print api.message

	# all done, thank you
	return True


print 'FAQ GENERATOR'
print '\n' + ('- ' * 8) + '\n'

# run until an FAQ is successfully generated
success = False
tries = 0
while not success:
	try:
		success = run()
	except:
		# something went wrong :(
		pass
	
	print '\n' + ('- ' * 8) + '\n'
	
	tries += 1
	if tries > max_tries:
		print 'max tries reached, quitting for now :(' + '\n'
		break;
	

# all done
print 'ALL DONE!' + '\n\n'
exit()


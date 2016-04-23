

import re

k = 'Speech is a complex activity; as a result, errors are often made in speech. That is too bad, and very sad.'
rest = ''
parts = re.split('(\. |\? |! |; )', k)
print parts

if len(parts) > 1:
	k = parts[0] + parts[1].strip()
	if k[-1] in '.!?;':
		k = k[:-1]

	for part in parts[2:]:
		part = part.strip()
		rest += part
		if part == '.' or part == '!' or part == '?' or part == ';':
			rest += ' '
print k
print rest



"""import re, urllib2, json

def countable_noun(thing):
	'''
	searches Google NGram to see if a word in countable/mass noun
	returns True if countable, False if not

	ex: cats are countable (many cats)
	    bread is not (much bread)
	'''

	# format into url (replace spaces with + for url)
	thing = re.sub(' ', '\+', thing)
	url = 'https://books.google.com/ngrams/graph?content=many+' + thing + '%2C+much+' + thing + '&year_start=1800&year_end=2000'
	response = urllib2.urlopen(url)
	html = response.read()

	# extract timeseries data from html source
	# put spaces back again :)
	thing = re.sub('\+', ' ', thing)
	many_data = json.loads(re.search('\{"ngram": "many ' + thing + '".*?\}', html).group(0))['timeseries']
	many = sum(many_data) / float(len(many_data))

	much_data = json.loads(re.search('\{"ngram": "much ' + thing + '".*?\}', html).group(0))['timeseries']
	much = sum(much_data) / float(len(much_data))

	# return True if countable; False if not
	if many > much:
		return True
	return False

print countable_noun('cats')
"""

# question = 'This my friend'

# if question.count('"') % 2 != 0:
# 	question += '"'
# if question.count('(') != question.count(')'):
# 	question += ')'
# print question




# import wikipedia, re
# from random import choice, random
# from pattern.en import tag, singularize, pluralize

# s = 'Several carrots sat on a nice carrot field.'

# matches = re.finditer('carrot', s)
# print matches

# for m in matches:
# 	print m.group(0)


'''
chance_wrong_question = 0.0
chance_wrong_word = 	0.3
pick_best = 			True

things = 	[ 'michigan', 'christmas', 'carrot', 'cat', 'baywatch' ]
thing =     things[0]


# find matching articles
print 'searching Wikipedia...'
all_articles = wikipedia.search(thing)
articles = [ a for a in all_articles if not a.startswith('List of ') and not a.endswith('(disambiguation)') ]
if pick_best:
	print 'selecting most likely article...'
	article = wikipedia.page(articles[0])
else:
	print 'selecting random article...'
	article = wikipedia.page(choice(articles))


# title of article 
print 'extracting title...'
thing = article.title
thing = re.sub(r' \(.*?\)', '', thing)			# strip ()
thing = thing.lower()
print '- ' + thing


# clean up article content for search
print 'getting article...'
content = article.content
content = re.sub(r' \(.*?\) ', ' ', content)	# nothing in ()


# words for random wrong questions (which result in right answers)
with open('../WordLists/SingularNouns.txt') as f:
	singular_nouns = f.readlines()
with open('../WordLists/PluralNouns.txt') as f:
	plural_nouns = f.readlines()


# get singular and plural form
singular = singularize(thing)
plural =   pluralize(thing)
print 'thing: ' + singular + '/' + plural + '\n'


# get things known
print 'extracting knowledge...'
sentences = []
for m in re.finditer('(' + thing + '|' + plural + '|' + singular + ')' + ' (is|are|were|was)(.*?\w{2,})\.', content, re.IGNORECASE):
	sentence = 	  m.group(0).strip()
	subject = 	  m.group(1).strip()
	connector =   m.group(2).strip()

	# give wrong question?
	wrong_question = False
	if random() < chance_wrong_question:
		wrong_question = True

	# if a longer sentence, split into two parts
	known = ''
	wrong = ''
	rest = None
	hit_wrong_word = False
	tagged = tag(m.group(3).strip(), tokenize=False)
	for i, (word, pos) in enumerate(tagged):
		pos = re.sub(r'-.*?$', '', pos)
		break_at = [ 'IN', 'RB', 'CC' ]
		whitelist = [ 'of' ]
		if pos in break_at and word not in whitelist:
			rest = ' '.join([ word for word, pos in tagged[i:] ])
			break
		else:
			known += word + ' '
			s_nouns = [ 'NN', 'NNP', 'NNPS' ]
			p_nouns = [ 'NNS' ]
			if wrong_question and random() < chance_wrong_word and (pos in s_nouns or pos in p_nouns):
				if pos in s_nouns:
					word = choice(singular_nouns).strip()
				else:
					word = choice(plural_nouns).strip()
				if not hit_wrong_word:
					first_wrong = word
				hit_wrong_word = True
			wrong += word + ' '
	known = known.strip()
	wrong = wrong.strip()

	# format into question/answer
	if not wrong_question or not hit_wrong_word:
		question = connector.title() + ' ' + subject.lower() + ' ' + known + '?'
		answer = 'Yes'
		if rest != None:
			answer += ', ' + rest
		answer += '.'
	else:
		a_an = 'a'
		if first_wrong[0] in 'aeiou':
			a_an = 'an'
		question = connector.title() + ' ' + subject.lower() + ' ' + a_an + ' type of ' + first_wrong + '?'
		question = connector.title() + ' ' + subject.lower() + ' sometimes known as ' + a_an + ' ' + first_wrong + '?'
		answer = 'No, ' + subject.lower() + ' ' + connector + ' ' + known
		if rest != None:
			answer += ', ' + rest
		answer += '.'

	# add to list
	sentences.append( { 'sentence': sentence, 'subject': subject, 'connector': connector, 'known': known.strip(), 'rest': rest, 'question': question, 'answer': answer } )

print '- learned ' + str(len(sentences)) + ' things' + '\n'

# show us the Q&A!
for s in sentences:
	print 'Q: ' + s['question']
	print 'A: ' + s['answer']
	print ''

'''
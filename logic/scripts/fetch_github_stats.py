import requests
import collections
from config import constants
from database import db, db_models, db_common
from tools import db_utils

def fetch():

	organization = "OriginProtocol"
	credentials = (None, constants.GITHUB_KEY)

	repos_url = 'https://api.github.com/orgs/%s/repos' % (organization)
	repos = requests.get(repos_url, auth=credentials)

	counts = collections.defaultdict(int)
	pics = collections.defaultdict(str)

	# we don't count contributors from detached forked projects (ie. origin-docs)
	special_forked = ["origin-docs"]

	print 'checking non-forked repos first:'
	for repo in repos.json():
		if not repo['fork'] and repo['name'] not in special_forked:

			# count pulls
			pulls_url = 'https://api.github.com/repos/%s/%s/pulls' % (organization, repo['name'])
			results = requests.get(pulls_url, auth=credentials)

			print repo['name']
			stats_url = 'https://api.github.com/repos/%s/%s/stats/contributors' % (organization, repo['name'])
			results = requests.get(stats_url, auth=credentials)
			try:
				data = results.json()

				for author in data:
					# print '\t%s\t%s\t%s' % (author['author']['login'],author['total'], author['author']['avatar_url'])
					counts[author['author']['login']] = counts[author['author']['login']] + author['total']
					pics[author['author']['login']] = author['author']['avatar_url']
			except Exception as e:
				print(e)
				print("Skipping...")

	# only include contributions from contributors who have also contributed to non-forked repos
	print 'checking forked & special-case repos:'
	for repo in repos.json():
		if repo['fork'] or repo['name'] in special_forked:
			print repo['name']
			stats_url = 'https://api.github.com/repos/%s/%s/stats/contributors' % (organization, repo['name'])
			results = requests.get(stats_url, auth=credentials)
			data = results.json()

			for author in data:
				# if repo['name'] in forked:
				if author['author']['login'] not in counts:
					continue
				counts[author['author']['login']] = counts[author['author']['login']] + author['total']
				pics[author['author']['login']] = author['author']['avatar_url']

	total_commits = 0

	for row, value in counts.iteritems():
		user = db_common.get_or_create(db.session, db_models.Contributor, username=row)
		user.commits = value
		user.avatar = pics[row]

		print row + '\t' + str(value) + '\t' + pics[row]
		total_commits += value

	print '%s commits' % total_commits 
	print '%s contributors' % len(counts)

with db_utils.request_context():
	fetch()
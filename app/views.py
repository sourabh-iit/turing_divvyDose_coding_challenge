from flask_restful import Resource
from flask import current_app as app

import requests

from .exception import ValidationError, UnExepectedError


class MergeProfile(Resource):
  def get(self, profile_name):
    try:
      github_info = self.get_github_org_info(profile_name)
      bitbucket_info = self.get_bitbucket_org_info(profile_name)
      return self.merge_info(github_info, bitbucket_info)
    except ValidationError as e:
      return e.args[0], 400
    except UnExepectedError as e:
      app.logger.exception(str(e))
      return "Unexpected error occurred. Please try again later", 400

  def merge_info(self, github_info, bitbucket_info):
    """ Returns merged info from github and bitbucket """
    merged_info = github_info
    merged_info['public_repos']['original'] += bitbucket_info['public_repos']['original']
    merged_info['public_repos']['forked'] += bitbucket_info['public_repos']['forked']
    merged_info['watchers_count'] += bitbucket_info['watchers_count']
    merged_info['languages'].extend(bitbucket_info['languages'])
    merged_info['topics'].extend(bitbucket_info['topics'])
    merged_info['languages'] = list(set(merged_info['languages']))
    merged_info['topics'] = list(set(merged_info['topics']))
    return merged_info

  def get_github_org_info(self, org):
    """" Returns github required info from all public repos accessible by org """
    url = f'{app.config["GITHUB_API_ENDPOINT"]}/orgs/{org}/repos'
    repos = self.get_github_public_repos(url)
    org_info = {
      'public_repos': {
        'original': 0,
        'forked': 0
      },
      'watchers_count': 0,
      'languages': [],
      'topics': []
    }
    for repo in repos:
      if repo['fork']:
        org_info['public_repos']['forked'] += 1
      else:
        org_info['public_repos']['original'] += 1
      org_info['watchers_count'] += repo['watchers_count']
      org_info['topics'].extend(repo.get('topics', []))
      org_info['languages'].extend(self.get_repo_languages(repo['languages_url']))
    return org_info
  
  def get_bitbucket_org_info(self, team):
    """ Returns info bitbucket public repos accessible by team """
    url = f'{app.config["BITBUCKET_API_ENDPOINT"]}/repositories/{team}'
    repos = self.get_bitbucket_public_repos(url)
    org_info = {
      'public_repos': {
        'original': 0,
        'forked': 0
      },
      'watchers_count': 0,
      'languages': [],
      'topics': []
    }
    for repo in repos:
      if 'parent' in repo:
        org_info['public_repos']['forked'] += 1
      else:
        org_info['public_repos']['original'] += 1
      org_info['watchers_count'] += self.get_bitbucket_watchers_count(repo['links']['watchers']['href'])
      org_info['languages'].append(repo['language'])
    return org_info

  def get_github_public_repos(self, url):
    """ Returns public repos by recursively calling function using next link in response header """
    res = self.request_github_url(url, headers={"Accept":"application/vnd.github.mercy-preview+json"})
    if res.status_code == 200:
      repos = [repo for repo in res.json() if not repo.get('private')]
      headers = res.headers
      # Look for multiple pages
      if 'Link' in headers:
        for link in headers.get('Link').split(','):
          if "next" in link:    # if there is next page
            url = link.split(';')[0].strip()[1:-1]
            repos.extend(self.get_github_public_repos(url))
      return repos
    elif res.status_code==404:
      raise ValidationError('Organization name does not exists - Github')
    raise UnExepectedError

  def get_bitbucket_public_repos(self, url):
    """ Returns public repos from bitbucket by recursively calling function using next url in response """
    res = self.request_bitbucket_url(url)
    if res.status_code==200:
      result = res.json()
      repos = [repo for repo in result['values'] if not repo['is_private']]
      if 'next' in result:
        repos.extend(self.get_bitbucket_public_repos(result['next']))
      return repos
    elif res.status_code == 404:
      raise ValidationError('Team name does not exist - Bitbucket')
    raise UnExepectedError

  def get_bitbucket_watchers_count(self, url):
    """ Returns watchers count by traversing pages """
    res = self.request_bitbucket_url(url)
    if res.status_code==200:
      result = res.json()
      count = result['pagelen']
      if 'next' in result:
        count += self.get_bitbucket_watchers_count(result['next'])
      return count
    raise UnExepectedError

  def request_github_url(self, url, headers={}):
    """ Requests github api using baisc authentication """
    auth = (app.config['GITHUB_USERNAME'], app.config['GITHUB_PASSWORD'])
    res = requests.get(url, auth=auth, headers=headers)
    return res

  def get_repo_languages(self, url):
    res = self.request_github_url(url)
    if res.status_code == 200:
      return res.json().keys()
    raise UnExepectedError

  def request_bitbucket_url(self, url):
    return requests.get(url)
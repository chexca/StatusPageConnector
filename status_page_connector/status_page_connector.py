""" Wrapper for Status Page API"""
import logging
import requests
import json

DEFAULT_API_URL = 'https://api.statuspage.io/v1/pages/'


class StatusPageConnector(object):
	
	def __init__(self, page_id, key, api_url=DEFAULT_API_URL):
		self.page_id = page_id
		self.key = key
		self.api_url = api_url

	def connect(self, module='', method='get', post_params=None):
		"""Method for querying the Status Page API.

		:param module: Status Page module to be retrieved.
		:type module: basestring
		:param method: HTTP Method used in the request.
		:type method: basestring
		:param post_params: Parameters to be sent through a POST request
		:type post_params: dict
		:return: Response of the API
		:rtype: requests.models.Response
		"""

		full_url = self.api_url + self.page_id + module + '.json'
		header = {'Authorization': 'OAuth ' + self.key}
		allowed_methods = ['get', 'post', 'delete', 'patch']
		if method in allowed_methods:
			response = requests.request(method=method, url=full_url, headers=header, params=post_params)
		else:
			return "Method is not valid. Allowed methods are 'GET', 'POST', 'PATCH' and 'DELETE'"
		return response
	
	def get_incidents(self):
		"""Getting the incidents stored by your Status Page instance.

		:return: incidents of your Status Page account.
		:rtype: requests.models.Response
		"""
		return self.connect('/incidents')

	def get_page_profile(self):
		"""Getting the profile of your Status Page instance.

		:return: profile of your Status Page account.
		:rtype: requests.models.Response
		"""
		return self.connect()

	def update_page_profile_attribute(self, attribute, value):
		post_params = {'page[' + attribute + ']': value}
		response = self.connect(module='', method='patch', post_params=post_params)
		if response.status_code == 201:
			return self.parse_response(response)
		else:
			return "Something went wrong, check out this error: " + response.content
	
	def get_components(self):
		"""Getting the components stored by your Status Page instance.

		:return: components of your Status Page account.
		:rtype: requests.models.Response
		"""
		return self.connect('/components')

	def get_all_subscribers(self):
		"""Getting the users subscribed to your Status Page instance.

		:return: subscribers of your Status Page account.
		:rtype: requests.models.Response
		"""
		return self.connect('/subscribers')

	def get_non_sms_subscribers(self):
		"""Getting the users subscribed to your Status Page instance without a phone number set.

		:return: subscribers without phone number of your Status Page account.
		:rtype: requests.models.Response
		"""
		all_subscribers = self.parse_response(self.get_all_subscribers())
		non_sms_subscribers = []
		for subscriber in all_subscribers:
			if 'phone_number' not in subscriber.keys():
				non_sms_subscribers.append(subscriber)
		return non_sms_subscribers
	
	def get_subscribers_for_incident(self, incident_id):
		"""Getting the users subscribed to a certain incident of your Status Page account.

		:return: users subscribed to a certain incident of your Status Page account.
		:rtype: requests.models.Response
		"""
		return self.connect('/incidents/' + incident_id + '/subscribers')

	def get_metrics(self):
		"""Getting the metrics stored by your Status Page instance.

		:return: metrics of your Status Page account.
		:rtype: requests.models.Response
		"""
		return self.connect('/metrics_providers')
	
	def delete_subscriber(self, subscriber_id):
		"""Delete a subscriber from your Status Page instance.

		:return: The status of the operation of deleting an user of your Status Page account.
		:rtype: requests.models.Response
		"""
		url_delete = '/subscribers/' + subscriber_id
		return self.connect(url_delete, 'delete')
	
	def get_subscriber_by_email(self, subscriber_email):
		"""Get a subscriber of your Status Page account using an email.

		:param subscriber_email: email used for creating the subscriber
		:type subscriber_email: basestring
		:return: A dict with the subscriber information or an error message
		:rtype: dict | basestring
		"""
		all_subscribers = self.parse_response(self.get_all_subscribers())
		for subscriber in all_subscribers:
			if subscriber.get('email', None) and subscriber.get('email') == subscriber_email:
				return subscriber
		return "ERROR - This email does not belong to any subscriber"

	def create_subscriber_using_email(self, email):
		"""Create a subscriber in your Status Page account using an email.

		:param email: email of the new subscriber
		:type email: basestring
		:return: A dictionary with the subscriber information or an error message
		:rtype: dict | basestring
		"""
		post_params = {'subscriber[email]': email, 'subscriber[skip_confirmation_notification]': True}
		response = self.connect(module='/subscribers', method='post', post_params=post_params)
		if response.status_code == 201:
			return self.parse_response(response)
		else:
			return "Something went wrong, check out this error: " + response.content

	@staticmethod
	def parse_response(response):
		return json.loads(response.content)


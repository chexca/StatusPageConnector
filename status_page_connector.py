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
		full_url = self.api_url + self.page_id + module + '.json'
		header = {'Authorization': 'OAuth ' + self.key}
		allowed_methods = ['get', 'post', 'delete', 'patch']
		if method in allowed_methods:
			response = requests.request(method=method, url=full_url, headers=header, params=post_params)
		else:
			return "Method is not valid. Allowed method are 'get', 'post' and 'delete'"
		return response
	
	def get_incidents(self):
		return self.connect('/incidents')

	def get_page_profile(self):
		return self.connect()

	def update_page_profile_attribute(self, attribute, value):
		post_params = {'page[' + attribute + ']': value}
		response = self.connect(module='', method='patch', post_params=post_params)
		if response.status_code == 201:
			return self.parse_response(response)
		else:
			return "Something went wrong, check out this error: " + response.content
	
	def get_components(self):
		return self.connect('/components')

	def get_all_subscribers(self):
		return self.connect('/subscribers')

	def get_non_sms_subscribers(self):
		all_subscribers = self.parse_response(self.get_all_subscribers())
		non_sms_subscribers = []
		for subscriber in all_subscribers:
			if not 'phone_number' in subscriber.keys():
				non_sms_subscribers.append(subscriber)
		return non_sms_subscribers
	
	def get_subscribers_for_incident(self, incident_id):
		return self.connect('/incidents/' + incident_id + '/subscribers')

	def get_metrics(self):
		return self.connect('/metrics_providers')
	
	def delete_subscriber(self, subscriber_id):
		url_delete = '/subscribers/' + subscriber_id
		return self.connect(url_delete, 'delete')
	
	def get_subscriber_by_email(self, subscriber_email):
		all_subscribers = self.parse_response(self.get_all_subscribers())
		for subscriber in all_subscribers:
			if subscriber.get('email', None) and subscriber.get('email') == subscriber_email:
				return subscriber
		return "ERROR - This email does not belong to any subscriber"

	def create_subscriber_using_email(self, email):
		post_params = {'subscriber[email]': email,
					   'subscriber[skip_confirmation_notification]': True}
		response = self.connect(module='/subscribers', method='post', post_params=post_params)
		if response.status_code == 201:
			return self.parse_response(response)
		else:
			return "Something went wrong, check out this error: " + response.content

	def parse_response(self, response):
		return json.loads(response.content)


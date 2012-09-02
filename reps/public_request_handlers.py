from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import users
from reps.model.model import RepsUser
import os

class RepsRequestHandler(webapp.RequestHandler):
	
	def __init__(self):
		webapp.RequestHandler.__init__(self)
		self.template_path = ''
		self.template_vars = {}
		self.user = None
		self.reps_user = None
		self.errors = []
		self.messages = []
		#####################################
		
		self.user = users.get_current_user()
		self.template_vars['errors'] = self.errors
		self.template_vars['messages'] = self.messages
		
		if self.user:
			try:
				self.reps_user = RepsUser.all().filter('user =', self.user).fetch(1)[0]
				self.template_vars['reps_user'] = self.reps_user
			except IndexError:
				pass #the user hasn't created a profile
				
			self.template_vars['logout_url'] = users.create_logout_url('//')
		else:
			self.template_vars['login_url'] = users.create_login_url('/users/home')
	
	def dispatch(self):
		self.response.out.write(template.render(self.template_path, self.template_vars))
	
	def get(self, requested_page): #this will typically be overriden by any subclass
		requested_page = requested_page.lower()
		if requested_page == '':
			self.template_path = os.path.join(os.path.dirname(__file__), 'index.html')
		elif requested_page == 'about':
			self.template_path = os.path.join(os.path.dirname(__file__), 'about.html')
		else:
			self.template_path = os.path.join(os.path.dirname(__file__), '404.html')
			
		self.dispatch()
		
		

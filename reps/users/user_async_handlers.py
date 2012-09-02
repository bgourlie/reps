from google.appengine.ext import db
from google.appengine.ext import webapp
from reps.model.model import Exercise
class ExerciseCreate_AddExerciseHTML(webapp.RequestHandler):
	def post(self):
		self.response.headers['Content-Type'] = 'plain/text'
		exercise_key_string = self.request.get('exercise_key')
		exercise = None
		html = ''
		
		try:
			exercise = Exercise.get(db.Key(exercise_key_string))
		except db.BadKeyError:
			html = 'error'
			self.response.out.write(html)
			return 
			
		html = "<tr><td>" + exercise.name + "</td><td><input type='text' /></td></tr>"
		self.response.out.write(html)

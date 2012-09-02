from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template   
from google.appengine.ext import db
import os
import re
import datetime
from reps.util import workout_util, reps_util
from reps.model.model import Exercise, WorkoutExercise, ExerciseRecord, Workout, RepsUser, WorkoutRecord
from public_request_handlers import RepsRequestHandler

class WorkoutCreateOrEdit(RepsRequestHandler):
	def get(self):
		self.template_path = os.path.join(os.path.dirname(__file__), 'workout_create_or_edit.html')

		workout_key_string = self.request.get('edit')
		exercises = Exercise.all()
		self.template_vars['exercises'] = exercises
		#this is set if we are editing a workout
		if workout_key_string:
			try:
				workout = Workout.get(db.Key(workout_key_string))
			except db.BadKeyError:
				self.errors.append('The specified workout is invalid')
		 		self.dispatch()
				return
			
			#make sure they aren't trying to edit
			#someone elses workout
			if workout.user != self.user:
				raise "PossibleHackingException"
			
			workout_exercises = WorkoutExercise.gql('WHERE workout = :1', workout)
			self.template_vars['workout'] = workout
			self.template_vars['workout_exercises'] = workout_exercises
			
 		self.dispatch()
		
	def post(self):
		self.template_path = os.path.join(os.path.dirname(__file__), 'workout_create_or_edit.html')
		exercise_key_strings = self.request.get('exercise_keys', allow_multiple=True)
		workout_name = self.request.get('workout_name')
		tag_strings = filter(reps_util.emptyFilter, self.request.get('tags',allow_multiple=True))
		workout_to_edit_key = self.request.get('edit_workout')
		workout = None
		workout_exercises_to_delete = []
		exercises = []
		
		if len(exercise_key_strings) == 0 \
		or len(workout_name) < 4:
			raise "WorkoutCreateException"
				
		for exercise_key_string in exercise_key_strings:
			exercises.append(Exercise.get(db.Key(exercise_key_string)))
			
		if workout_to_edit_key:
			try:
				workout = Workout.get(db.Key(workout_to_edit_key))
				if workout.user != self.user: raise db.BadKeyError
			except db.BadKeyError:
				raise "PossibleHackingException"
		try:
			existing_workout = Workout.gql('WHERE user = :1 AND name = :2', self.user, workout_name).fetch(1)[0]
			if (existing_workout and not workout) or (workout.key() != existing_workout.key()):
				self.errors.append('A workout already exists with the name <b>' + workout_util.workout_edit_link(existing_workout, existing_workout.name) + '</b>.  Click the link to edit it.')
				self.get()
				return
		except IndexError:
			pass #it's ok to be here, means that the workout with the same name doesn't exist
		
		#generate our tag properties from the strings
		tags = []
		for tag_string in tag_strings:
			tags.append(db.Category(tag_string))
		
		if workout: #we are editing the existing workout
			workout.name = workout_name
			workout.tags = tags
			workout_exercises_to_delete = WorkoutExercise.gql('WHERE workout = :1', workout)
		else: #we are creating a new workout
			workout = Workout(user=self.user,name=workout_name,tags=tags)
		
		try:
			db.run_in_transaction(self.__save_workout, workout, exercises, workout_exercises_to_delete)
		except db.Rollback:
			self.errors.append('There was an error saving the workout')
			self.get()
			return
			
		self.messages.append('Your workout was successfully saved!')
		self.get()
		
	def __save_workout(self, workout, exercises, workout_exercises_to_delete):
		#if this is an existing workout we delete all the old WorkoutExercises
		for workout_exercise in workout_exercises_to_delete:
			workout_exercise.delete()
			
		workout.put()
		i = 0
		for exercise in exercises:
			i = i + 1
			workout_exercise = WorkoutExercise(workout=workout,exercise=exercise,parent=workout)
			#set dynamic properties
			workout_exercise.exercise_order = i
			workout_exercise.put()
				
class WorkoutAdvancedEdit(RepsRequestHandler):
	pass

class WorkoutLog(RepsRequestHandler):
	def get(self):
		self.template_path = os.path.join(os.path.dirname(__file__), 'workout_log.html')

		if self.request.get('workout'):
			workout_key = self.request.get('workout')
		
		if not workout_key:
			self.errors.append('No workout was specified.')
			self.dispatch()
			return
		
		workout = Workout.get(db.Key(workout_key))
		workout_exercises = WorkoutExercise.gql('WHERE workout = :1', workout)
		self.template_vars['workout_exercises'] = workout_exercises
		self.template_vars['workout_key'] = workout_key
		self.dispatch()
	
	def post(self):
		workout_key = self.request.get('workout_key')
		workout_exercise_keys = self.request.get('workout_exercises', allow_multiple=True)
		year = int(self.request.get('year'))
		month = int(self.request.get('month'))
		day = int(self.request.get('day'))
		try:	
			date = datetime.date(year, month, day)
		except ValueError:
			#invalid date, probably the day has been set too high
			#for a month like February, for example February 31 
			self.errors.append('The specified date was invalid.')
			self.get()
			return
		try:
			workout = Workout.get(db.Key(workout_key))
		except db.BadKeyError:
			raise "PossibleHackingAttempt"
			
		workout_record = WorkoutRecord(user=self.user,date=date,workout=workout)
		
		exercise_record_data = []
		for workout_exercise_key in workout_exercise_keys:
			weights = self.request.get(workout_exercise_key + '_weight', allow_multiple=True)			
			reps_ = self.request.get(workout_exercise_key + '_reps', allow_multiple=True)
			
			# make sure no one is fussin with keys to muss things up 
			try:
				workout_exercise = WorkoutExercise.get(db.Key(workout_exercise_key))
				if workout_exercise.workout.key() != workout.key():
					raise "PossibleHackingAttempt"
			except db.BadKeyError:
				raise "PossibleHackingAttempt"

			er_data = {}
			er_data['workout_exercise'] = workout_exercise
			for weight, reps in zip(weights, reps_):
				er_data['dynamic_properties'] = {}
				er_data['dynamic_properties']['weight'] = float(weight)
				er_data['dynamic_properties']['reps'] = int(reps)
				exercise_record_data.append(er_data)
		
		try:
			db.run_in_transaction(self.__save_workout_record, workout_record, exercise_record_data)
		except db.Rollback:
			self.errors.append('There was an error while trying to save your workout.')
			self.get()
			return
		
		self.redirect('/Wherever_we_go_from_here')
	
	def __save_workout_record(self, workout_record, exercise_record_data):
		workout_record.put()
		
		for data in exercise_record_data:
			exercise_record = ExerciseRecord(workout_exercise=data['workout_exercise'],workout_record=workout_record,parent=workout_record)
			for prop in data['dynamic_properties']:
				setattr(exercise_record,prop,data['dynamic_properties'][prop])
			exercise_record.put()
class MyWorkouts(RepsRequestHandler):
		
	def get(self):
		self.template_path = os.path.join(os.path.dirname(__file__), 'my_workouts.html')

		workout_results = Workout.all().filter('user =', self.user)
		
		workouts = []
		for workout in workout_results:
			workouts.append(workout)
		if len(workouts) == 0:
			workouts = None
				
		self.template_vars['workouts'] = workouts
		self.dispatch()
		
class WorkoutPrintLog(RepsRequestHandler):
	def get(self):
		self.template_path = os.path.join(os.path.dirname(__file__), 'workout_print_log.html')
		workout_key_string = self.request.get('workout')
		
		try:
			workout = Workout.get(db.Key(workout_key_string))
		except db.BadKeyError:
			raise "WorkoutPrintLogException"
		
		self.template_vars['workout'] = workout
		self.template_vars['workout_exercises'] = workout_util.get_workout_exercises(workout)
		self.dispatch()

class UserHome(RepsRequestHandler):
	def get(self):
		recent_workouts = WorkoutRecord.gql('WHERE user = :1 order by date desc limit 5', self.user).fetch(5)
		if len(recent_workouts) == 0:
			recent_workouts = None
			
		self.template_vars['recent_workouts'] = recent_workouts
		self.template_path = os.path.join(os.path.dirname(__file__), 'user_home.html')
		self.dispatch()

class WorkoutLogView(RepsRequestHandler):
	def get(self):
		self.template_path = os.path.join(os.path.dirname(__file__), 'workout_log_view.html')
		self.dispatch()

class WorkoutView(RepsRequestHandler):
	def get(self):
		workout_key = self.request.get('workout')
		
		try:
			workout = Workout.get(db.Key(workout_key))
		except db.BadKeyError:
			raise "PossibleHackingAttempt"
		
		workout_exercises = WorkoutExercise.all().filter('workout =', workout)
		
		self.template_vars['workout'] = workout
		self.template_vars['workout_exercises'] = workout_exercises
		self.template_path = os.path.join(os.path.dirname(__file__), 'workout_view.html')
		self.dispatch()
	
class FirstLogin(RepsRequestHandler):
	def get(self, redirect_url):
		self.template_path = os.path.join(os.path.dirname(__file__), 'first_login.html')
		self.template_vars['redirect_url'] = redirect_url
		self.dispatch()
	
	def post(self, garbage):
		reps_user = None;
		nickname = self.request.get('nickname')
		redirect_url = self.request.get('redirect_url')

		#if self.reps_user is not None, then the super class found a reps_user
		#in which case they should not be creating another
		if self.reps_user or re.match('^[a-zA-Z0-9_]{4,28}$',nickname) is None:
			raise "FirstLoginException"
		
		#check to see that the user name isn't already taken
		try:
			reps_user = RepsUser.all().filter('nickname =', nickname).fetch(1)[0]
		except IndexError:
			pass #we want this
		
		if reps_user:
			self.errors.append('This nickname is not available.  Please choose another.')
			self.get(redirect_url)
			return
			
		RepsUser(user=self.user,nickname=nickname).put()
		self.redirect(redirect_url)


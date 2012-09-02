from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
import os
from reps.model.model import Exercise, Muscle, ExerciseMuscle
from reps.util import exercise_util, muscle_util, reps_util
from public_request_handlers import RepsRequestHandler

class AdminIndex(RepsRequestHandler):
	def get(self):
		self.template_path = os.path.join(os.path.dirname(__file__), 'index.html')
 		self.dispatch()

class ExerciseDelete(RepsRequestHandler):
	def get(self):
		
		exercise_key_str = self.request.get('exercise')
		try:
			exercise = Exercise.get(db.Key(exercise_key_str))
		except db.BadKeyError:
			#Yes - we are raising the same exception we are catching
			#We want to error out, and we want to programmatically check
			#When we get around to implementing custom exceptions, 
			#this will be replaced
			raise db.BadKeyError
		
		exercise_muscles = exercise_util.get_exercise_muscles(exercise)
		db.run_in_transaction(self.__delete_exercise, exercise, exercise_muscles)
		self.redirect(self.request.headers['Referer'])
		
	def __delete_exercise(self, exercise, exercise_muscles):
		exercise.delete()
		if len(exercise_muscles) > 0:
			for exercise_muscle in exercise_muscles:
				exercise_muscle.delete()
		
class ExerciseView(RepsRequestHandler):
	def get(self):
		exercise_key_str = self.request.get('exercise')
		try:
			exercise = Exercise.get(db.Key(exercise_key_str))
		except db.BadKeyError:
			#Yes - we are raising the same exception we are catching
			#We want to error out, and we want to programmatically check
			#When we get around to implementing custom exceptions, 
			#this will be replaced
			raise db.BadKeyError
		
		exercise_muscles = exercise_util.get_exercise_muscles(exercise)
		self.template_vars['exercise'] = exercise
		self.template_vars['exercise_muscles'] = exercise_muscles
		self.template_path = os.path.join(os.path.dirname(__file__), 'exercise_view.html')
		self.dispatch()

class ExerciseCreateOrEdit(RepsRequestHandler):
	def get(self):
		exercise_to_edit = self.request.get('edit')
    	
		if exercise_to_edit:
			try:
				exercise = Exercise.get(db.Key(exercise_to_edit))
				exercise_muscles = ExerciseMuscle.gql('WHERE exercise = :1', exercise)
				self.template_vars['exercise'] = exercise
				self.template_vars['exercise_muscles'] = exercise_muscles
			except db.BadKeyError:
				self.errors.append('The specified exercise could not be found.')
	    		
		muscleQuery = Muscle.all()
		self.template_vars['muscles'] = muscleQuery 
		self.template_path = os.path.join(os.path.dirname(__file__), 'exercise_create_or_edit.html')
		self.dispatch()
     	
	def post(self):
		muscles = self.request.get('muscles', allow_multiple=True)
		muscle_roles = filter(reps_util.emptyFilter, self.request.get('roles', allow_multiple=True))
		exercise_name = self.request.get('exercise_name')
		exercise_type_str = self.request.get('exercise_type')
		edit_exercise = self.request.get('edit_exercise')
		old_exercise_muscles = []
		
    		#data validation, we aren't going to give 
		#feedback since validation with feedback is
		#done on the client. 
		if len(muscles) == 0 or len(muscles) != len(muscle_roles) \
		or len(exercise_name) < 3 \
		or len(exercise_name) > 30 \
		or len(exercise_type_str) == 0:
			raise "ExerciseValidationError"
		
		try:
			muscle_roles.index('Target')
		except ValueError:
			raise "ExerciseValidationError"
		#validation complete
		
		#wait until after validation to assign this.
		#it will throw it's own exception if you pass
		#a null value to the Category constructor	
		exercise_type_cat = db.Category(exercise_type_str)
		
		if edit_exercise:
		#we are editing the exercise
			try:
				exercise = Exercise.get(db.Key(edit_exercise))
			except db.BadKeyError:
				#Yes - we are raising the same exception we are catching
				#We want to error out, and we want to programmatically check
				#When we get around to implementing custom exceptions, 
				#this will be replaced
				raise db.BadKeyError
				
			exercise.name = exercise_name
			exercise.type = exercise_type_cat
			
			#the following var used to store the ExerciseMuscle entities
			#related to the Exercise entity (if we are editing)
			#these are then passed to the save method so that
			#we can delete them safely within a transaction
			old_exercise_muscles = exercise_util.get_exercise_muscles(exercise)
		else:
			#check to see if an exercise already exists with this name
			#if not, create the new exercise
			try:
				existing_exercise = Exercise.gql('WHERE name = :1',exercise_name).fetch(1)[0]
				if existing_exercise:
					self.errors.append('An exercise already exists with the name ' + exercise_util.exercise_edit_link(existing_exercise) + '. Click the link to edit it.')
					self.get()
					return
			except IndexError:
				#this is what we want - it means the 
				#exercise name doesn't exist in the datastore
				pass
			#create the new exercise
			exercise = Exercise(name=exercise_name,type=exercise_type_cat)
			#todo: this should be put in the transaction below
			#when the app engine bug preventing root entities
			#and their decendants from being created in the
			#same transaction
			exercise.put()             
	        #server side validation
		found_target = False
		new_exercise_muscles = []
		for muscle_key, muscle_role in zip(muscles,muscle_roles):
			muscle = Muscle.get(db.Key(muscle_key))
			if muscle_role == 'Target':
				if found_target == True: #uh oh, more than one target defined, crap out
					raise "ExerciseValidationError" #yeah, no fancy feedback.  All that is done on the client. just die.
				else:
					found_target = True
					exercise.target_location = muscle.location 
			exercise_muscle = ExerciseMuscle(exercise=exercise,muscle=muscle,role=muscle_role,parent=exercise)
			new_exercise_muscles.append(exercise_muscle)
        
        #if we didn't have a target muscle for the exercise
        #once again, crap out with no feedback
		if found_target == False:
			raise "ExerciseValidationError"					                        	
	    
		#put the exercise again, so that we now save the target_location
		#super TODO - put this all in a transaction.
	    	exercise.put()
	    
	    #and now we're ready to commit the Exercise and ExerciseMuscle entities
	    #it is all isolated within a transaction                        
		try:
			db.run_in_transaction(self.__save_exercise_muscles, new_exercise_muscles, old_exercise_muscles)
			self.messages.append('Exercise <b>' + exercise.name + '</b> (' + exercise_util.exercise_edit_link(exercise) + ') has been successfully saved.')
		except db.Rollback:
			self.errors.append('A database error occured.  The exercise was not saved.')

		self.get()
	
	#we isolate the Exercise and ExerciseMuscle updates here so they can be run in a transaction
	def __save_exercise_muscles(self, new_exercise_muscles, old_exercise_muscles = []):
		
		#we delete all the many-to-many (ExerciseMuscle) entities and rebuild them.
		#this will only execute if the exercise already exists in the datastore 
		#(as in we are editing the entity)
		if len(old_exercise_muscles) > 0:
			for exercise_muscle in old_exercise_muscles:
				exercise_muscle.delete()
			
		#and add the new exercise muscles, voila		
		for exercise_muscle in new_exercise_muscles:
			exercise_muscle.put();

class ExerciseManage(RepsRequestHandler):
	def get(self):		
		exercises = Exercise.all()
		self.template_vars['exercises'] = exercises 
		self.template_path = os.path.join(os.path.dirname(__file__), 'exercises.html')
		self.dispatch()

class MuscleManage(RepsRequestHandler):
	def get(self):
		muscles = Muscle.all()
		self.template_vars['muscles'] = muscles
		self.template_path = os.path.join(os.path.dirname(__file__), 'muscles.html')
		self.dispatch()

class MuscleCreateOrEdit(RepsRequestHandler):
	def get(self,):

		muscle_to_edit = self.request.get('edit')
    	
		if muscle_to_edit:
			try:
				muscle = Muscle.get(db.Key(muscle_to_edit))
				self.template_vars['muscle'] = muscle
			except db.BadKeyError:
				self.errors.append('The specified muscle could not be found.')
		
		self.template_path = os.path.join(os.path.dirname(__file__), 'muscle_create_or_edit.html')
		self.dispatch()
	
	def post(self):
		muscle_name = self.request.get('muscle_name')
		muscle_location = self.request.get('muscle_location')
		muscle_to_edit = self.request.get('edit')
		
		#validation, no feedback just die
		if len(muscle_name) < 3 or len(muscle_name) > 50 \
		or len(muscle_location) == 0:
			raise "MuscleValidationError"
		
		if muscle_to_edit:
			try:
				muscle = Muscle.get(db.Key(muscle_to_edit))
			except db.BadKeyError:
				#Yes - we are raising the same exception we are catching
				#We want to error out, and we want to programmatically check
				#When we get around to implementing custom exceptions, 
				#this will be replaced
				raise db.BadKeyError
		else:	
			#make sure the muscle doesn't already exist
			#(programmatic unique constraint on the name property)
			try:
				existing_muscle = Muscle.gql('WHERE name = :1', muscle_name).fetch(1)[0]
				if existing_muscle:
					self.errors.append('An muscle already exists with the name ' + muscle_util.muscle_edit_link(existing_muscle, existing_muscle.name) + '. Click the link to edit it.')
					self.get()
					return
			except IndexError:
				pass #we wanna be here, this means no duplicate muscle name
			
			muscle = Muscle(name=muscle_name,location=muscle_location)
		try:
			db.run_in_transaction(self.__save_muscle,muscle)
		except db.Rollback:
			self.errors.append('There was an error saving the muscle to the database.')
		finally:
			self.get()

	def __save_muscle(self, muscle):
		muscle.put()

from google.appengine.ext import db

class Exercise(db.Model):
	name = db.StringProperty(required=True,multiline=False)
	type = db.CategoryProperty(required=True, choices=["Repetition", "Distance","Duration"])
	target_location = db.CategoryProperty()
	
class Muscle(db.Model):
	name = db.StringProperty(required=True,multiline=False)
	location = db.CategoryProperty(required=True,choices=["Neck", "Shoulders",
    								"Upper Arms", "Forearms",
    								"Back","Chest","Waist", "Hips", 
								"Thighs", "Calves"]) 													  												  
class ExerciseMuscle(db.Model):
	exercise = db.ReferenceProperty(Exercise,required=True)
	muscle = db.ReferenceProperty(Muscle,required=True)
	role = db.CategoryProperty(required=True, choices=["Target",
                                                        "Synergist",
                                                        "Dynamic Stabilizer",
                                                        "Stabilizer,",
                                                        "Antagonist Stabilizer"])

class RepsUser(db.Model):
	user = db.UserProperty(required=True)
	nickname = db.StringProperty(required=True,multiline=False)

class Workout(db.Model):
	name = db.StringProperty(required=True,multiline=False)
	tags = db.ListProperty(db.Category)
	user = db.UserProperty(required=False)

class WorkoutExercise(db.Expando):
	workout = db.ReferenceProperty(Workout,required=True)
	exercise = db.ReferenceProperty(Exercise, required=True)
	
	#dynamic properties we use:
		#set_number (int)
		#target_reps (double)
		#target_weight (float)
	
class WorkoutRecord(db.Model):
	user = db.UserProperty(required=True)
	date = db.DateProperty(required=True)
	workout = db.ReferenceProperty(Workout, required=True)

class ExerciseRecord(db.Expando):
	workout_exercise = db.ReferenceProperty(WorkoutExercise, required=True)
	workout_record = db.ReferenceProperty(WorkoutRecord, required=True)
	#dynamic properties we use:
		#reps (double)
		#weight (float)


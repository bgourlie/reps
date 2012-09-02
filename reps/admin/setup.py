from google.appengine.ext import db
from reps.model.model import Muscle, Exercise, ExerciseMuscle

def setup():
	#muscles list
	muscles = ["Sternocleidomastoid", "Splenius",
			   "Anterior Deltoid", "Lateral Deltoid", "Posterior Deltoid", "Supraspinatus",
			   "Triceps", "Biceps", "Brachialis",
			   "Brachioradialis", "Wrist Flexors", "Wrist Extensors", "Pronators", "Supinators",
			   "Latissimus Dorsi", "Teres Major", "Upper Trapezius", "Middle Trapezius", "Lower Trapezius", "Levator Scapulae", "Rhomboids", "Infraspinatus", "Teres Minor", "Subscapularis",
			   "Pectoralis Major, Sternal", "Pectoralis Major, Clavicular", "Pectoralis Minor", "Serratus Anterior",
			   "Rectus Abdominis", "Transverse Abdominus", "Obliques", "Quadratus Lumborum", "Erector Spinae",
			   "Gluteus Maximus", "Abductors", "Hip Flexors", "Deep External Rotators",
			   "Quadriceps", "Hamstrings", "Hip Adductors",
			   "Gastrocnemius", "Soleus", "Tibialis Anterior", "Popliteus"]
	#muscle locations, indexes correspond with the muscle list		 			
	m_locations = ["Neck", "Neck",
				   "Shoulders", "Shoulders", "Shoulders",
				   "Upper Arms", "Upper Arms", "Upper Arms",
				   "Forearms", "Forearms", "Forearms","Forearms","Forearms",
				   "Back", "Back", "Back", "Back", "Back", "Back", "Back", "Back", "Back", "Back",
				   "Chest", "Chest", "Chest", "Chest",
				   "Waist", "Waist", "Waist", "Waist", "Waist",
				   "Hips", "Hips", "Hips", "Hips",
				   "Thighs", "Thighs", "Thighs",
				   "Calves", "Calves", "Calves", "Calves"]
	
	#exercises
	exercises = ["Bench Press", "Pull-up", "Squat", "Deadlift"]
	
	#exercise types, indexes correspond with exercises list
	e_types = ["Repetition", "Repetition", "Repetition", "Repetition"]
	
	#exercise muscles, indexes correspond with exercises list
	e_muscles = [{'Target':['Pectoralis Major, Sternal'],
					'Synergist':['Pectoralis Major, Clavicular','Deltoid, Anterior','Triceps Brachii']},
				{'Target':['Latissimus Dorsi'],
					'Synergist':['Brachialis','Brachioradialis','Biceps Brachii','Teres Major','Rhomboids','Levator Scapulae','Trapezius, Lower','Pectoralis Major, Sternal','Pectoralis Minor'],
					'Dynamic Stabilizer':['Triceps, Long Head']},
				{'Target':['Quadriceps'],
					'Synergist':['Gluteus Maximus','Adductor Magnus','Soleus'],
					'Dynamic stabilizer':['Hamstrings','Gastrocnemius'],
					'Stabilizer':['Erector Spinae'],
					'Antagonist Stabilizer':['Rectus Abdominis','Obliques']},
				{'Target':['Gluteus Maximus'],
					'Synergist':['Quadriceps','Adductor Magnus','Soleus'],
					'Dynamic Stabilizer':['Hamstrings','Gastrocnemius'],
					'Stabilizer':['Erector Spinae','Trapezius, Middle','Trapezius, Upper','Levator Scapulae','Rhomboids'],
					'Antagonist Stabilizer':['Rectus Abdominis','Obliques']}]
	#stores the keys of the addeded exercises
	e_keys = []
	
	#stores the keys of the added muscles
	m_keys = []
				  
	print 'Content-Type: text/plain'			  
	print "Setting up reps..."
	
	print "Adding muscles to datastore..."
	for(muscle,location) in zip(muscles,m_locations):
		m_keys.append(Muscle(name=muscle,location=db.Category(location)).put())
		print 'Added muscle "%s" to datastore' % (muscle)
	
	print "Adding exercises to datastore..."
	for(exercise,type) in zip(exercises,e_types):
		e_keys.append(Exercise(name=exercise,type=db.Category(type)).put())
		print 'Added exercise "%s" to datastore' % (exercise)
		
	print "Done!"
	
db.run_in_transaction(setup)
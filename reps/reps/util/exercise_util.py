from reps.model.model import ExerciseMuscle

def get_exercise_muscles(exercise):
	exercise_muscles = ExerciseMuscle.all().filter('exercise =', exercise)
	em = []
	for exercise_muscle in exercise_muscles:
		em.append(exercise_muscle)
	return em

def exercise_edit_link(exercise, link_text='edit'):
	if exercise.is_saved():
		return '<a href="./exercise_create_or_edit?edit=' + exercise.key().__str__() + '">' + link_text + '</a>'	

def exercise_view_link(exercise, link_text='view'):
	if exercise.is_saved():
		return '<a href="./exercise_view?exercise=' + exercise.key().__str__() + '">' + link_text + '</a>'
		
def exercise_delete_link(exercise, link_text='delete'):
	if exercise.is_saved():
		return '<a href="./exercise_delete?exercise=' + exercise.key().__str__() + '">' + link_text + '</a>'
from reps.model.model import WorkoutExercise

def get_workout_exercises(workout):
	workout_exercises = WorkoutExercise.all().filter('workout =', workout)
	we = []
	for workout_exercise in workout_exercises:
		we.append(workout_exercise)
	return we
	
def workout_edit_link(workout, link_text='edit'):
	if workout.is_saved():
		return '<a href="./workout_create_or_edit?edit=' + workout.key().__str__() + '">' + link_text + '</a>'	

def workout_view_link(workout, link_text='view'):
	if workout.is_saved():
		return '<a href="./workout_view?workout=' + workout.key().__str__() + '">' + link_text + '</a>'
		
def workout_delete_link(workout, link_text='delete'):
	if workout.is_saved():
		return '<a href="./workout_delete?workout=' + workout.key().__str__() + '">' + link_text + '</a>'
		


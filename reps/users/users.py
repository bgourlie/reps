import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.api import users
from users.user_request_handlers import *
from users.user_async_handlers import *
from reps.model.model import RepsUser

#entrypoint
def main():
	
	#see if they have set up their reps profile information
	#todo: try and eliminate this bit of redundancy, we run this
	#query again every time a UserRequestHandler is instantiated
	try:
		RepsUser.all().filter('user =', users.get_current_user()).fetch(1)[0]
	except IndexError:
		application = webapp.WSGIApplication(
                                       [('(.*)', FirstLogin)],
                                       debug=True)
		wsgiref.handlers.CGIHandler().run(application)
		return
	
	application = webapp.WSGIApplication(
                                       [('/users/async/exercise_create-add_exercise_html', ExerciseCreate_AddExerciseHTML),
				       ('/users/home', UserHome),
				       ('/users/workout_create_or_edit', WorkoutCreateOrEdit),
				       ('/users/workout_advanced_edit', WorkoutAdvancedEdit),
				       ('/users/workout_log', WorkoutLog),
				       ('/users/workout_print_log', WorkoutPrintLog),
				       ('/users/my_workouts', MyWorkouts),
				       ('/users/workout_log_view', WorkoutLogView),
				       ('/users/workout_view', WorkoutView)],
                                       debug=True)
	
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == "__main__":
	main()
import wsgiref.handlers
from admin.admin_request_handlers import *

#entrypoint
def main():
  application = webapp.WSGIApplication(
                                       [('/admin/', AdminIndex),
                                        ('/admin/exercise_create_or_edit', ExerciseCreateOrEdit),
                                        ('/admin/exercise_delete', ExerciseDelete),
                                        ('/admin/exercise_view', ExerciseView),
                                        ('/admin/exercises', ExerciseManage),
                                        ('/admin/muscles', MuscleManage),
					('/admin/muscle_create_or_edit', MuscleCreateOrEdit)],
                                       debug=True)
  
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
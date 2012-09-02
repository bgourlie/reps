from reps.model.model import ExerciseMuscle

def muscle_edit_link(muscle, link_text='edit'):
	if muscle.is_saved():
		return '<a href="./muscle_create_or_edit?edit=' + muscle.key().__str__() + '">' + link_text + '</a>'	

def muscle_view_link(muscle, link_text='view'):
	if muscle.is_saved():
		return '<a href="./muscle_view?muscle=' + muscle.key().__str__() + '">' + link_text + '</a>'
		
def muscle_delete_link(muscle, link_text='delete'):
	if muscle.is_saved():
		return '<a href="./muscle_delete?muscle=' + muscle.key().__str__() + '">' + link_text + '</a>'

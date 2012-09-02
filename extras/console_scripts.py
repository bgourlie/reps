#list exercises and affected muscles
from exercise import Exercise
from muscle import MuscleRole

for exercise in Exercise.all():
  print exercise.name + ": "
  for mrk in exercise.muscles:
    mr = MuscleRole.get(mrk)
    print mr.muscle.name
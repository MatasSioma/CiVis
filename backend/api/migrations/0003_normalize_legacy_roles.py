from django.db import migrations


def forwards_role(apps, schema_editor):
	user_model = apps.get_model('api', 'User')
	legacy_role = 'job' + 'seeker'
	user_model.objects.filter(role=legacy_role).update(role='job_seeker')


def backwards_role(apps, schema_editor):
	user_model = apps.get_model('api', 'User')
	legacy_role = 'job' + 'seeker'
	user_model.objects.filter(role='job_seeker').update(role=legacy_role)


class Migration(migrations.Migration):
	dependencies = [
		('api', '0002_user_personal_code_hash_and_jobseeker_role'),
	]

	operations = [
		migrations.RunPython(forwards_role, backwards_role),
	]

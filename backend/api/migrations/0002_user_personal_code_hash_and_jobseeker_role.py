from django.db import migrations, models


def forwards_role(apps, schema_editor):
	user_model = apps.get_model('api', 'User')
	user_model.objects.filter(role='job_seeker').update(role='jobseeker')


def backwards_role(apps, schema_editor):
	user_model = apps.get_model('api', 'User')
	user_model.objects.filter(role='jobseeker').update(role='job_seeker')


class Migration(migrations.Migration):
	dependencies = [
		('api', '0001_initial'),
	]

	operations = [
		migrations.AddField(
			model_name='user',
			name='personal_code_hash',
			field=models.CharField(blank=True, max_length=64, null=True, unique=True),
		),
		migrations.RunPython(forwards_role, backwards_role),
		migrations.AlterField(
			model_name='user',
			name='role',
			field=models.CharField(
				choices=[('jobseeker', 'Job Seeker'), ('employer', 'Employer')],
				max_length=64,
			),
		),
		migrations.AddIndex(
			model_name='user',
			index=models.Index(
				fields=['personal_code_hash'], name='api_user_person_3d4420_idx'
			),
		),
	]

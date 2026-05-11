from django.db import migrations, models


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
		migrations.AddIndex(
			model_name='user',
			index=models.Index(
				fields=['personal_code_hash'], name='api_user_person_3d4420_idx'
			),
		),
	]

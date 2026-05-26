from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_alter_application_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
    ]

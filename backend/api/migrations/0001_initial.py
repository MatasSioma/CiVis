import pgvector.django
from django.db import migrations, models


class Migration(migrations.Migration):
	initial = True

	dependencies = []

	operations = [
		pgvector.django.VectorExtension(),
		migrations.CreateModel(
			name='Document',
			fields=[
				(
					'id',
					models.BigAutoField(
						auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
					),
				),
				('title', models.CharField(max_length=255)),
				('content', models.TextField(blank=True)),
				('embedding', pgvector.django.VectorField(blank=True, dimensions=1536, null=True)),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
			],
		),
	]

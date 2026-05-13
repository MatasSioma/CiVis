import pgvector.django.indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_merge_20260512_2044'),
    ]

    operations = [
        # No CV/Skill data needs to be preserved; truncate the CVSkill table so
        # the schema changes below can run cleanly (adding a non-null `name`,
        # `created_at`, `updated_at` would otherwise require defaults).
        migrations.RunSQL(
            sql='TRUNCATE TABLE api_cvskill;',
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RemoveConstraint(
            model_name='cvskill',
            name='cv_skill_unique',
        ),
        migrations.RemoveIndex(
            model_name='cvskill',
            name='idx_cv_skill_embedding',
        ),
        migrations.RemoveField(
            model_name='cv',
            name='skills',
        ),
        migrations.RemoveField(
            model_name='cvskill',
            name='skill',
        ),
        migrations.RemoveField(
            model_name='cvskill',
            name='years_of_experience',
        ),
        migrations.DeleteModel(
            name='Skill',
        ),
        migrations.AddField(
            model_name='cvskill',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AddField(
            model_name='cvskill',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='cvskill',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddConstraint(
            model_name='cvskill',
            constraint=models.UniqueConstraint(
                fields=('cv', 'name'), name='cv_skill_unique'
            ),
        ),
        migrations.AddIndex(
            model_name='cvskill',
            index=pgvector.django.indexes.HnswIndex(
                ef_construction=64,
                fields=['embedding'],
                m=16,
                name='idx_cv_skill_embedding',
                opclasses=['vector_cosine_ops'],
            ),
        ),
    ]

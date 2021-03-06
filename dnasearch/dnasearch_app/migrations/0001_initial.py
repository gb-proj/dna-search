# Generated by Django 3.1.2 on 2020-11-01 17:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DnaSearchRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_string', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='DnaSearch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_state', models.CharField(choices=[('SEARCHING', 'Searching'), ('FOUND', 'Found'), ('NOT_FOUND', 'Not found'), ('ERROR', 'Error')], max_length=16)),
                ('started_at', models.DateTimeField(verbose_name='datetime search was started')),
                ('completed_at', models.DateTimeField(verbose_name='datetime search was completed')),
                ('search_string', models.TextField()),
                ('result_protein', models.TextField()),
                ('result_start_location', models.IntegerField()),
                ('result_end_location', models.IntegerField()),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

# Generated by Django 2.2 on 2019-04-18 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('team_id', models.CharField(max_length=100, unique=True, verbose_name='Team ID')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('course_id', models.CharField(default=None, max_length=100, null=True, verbose_name='Course ID')),
                ('frontend_course_id', models.CharField(max_length=100, unique=True)),
                ('test_duration', models.PositiveIntegerField(blank=True, default=240, help_text='Test duration in minutes, default = 240 minute', null=True)),
                ('teams', models.ManyToManyField(default=None, null=True, to='trainer.Team')),
            ],
        ),
    ]

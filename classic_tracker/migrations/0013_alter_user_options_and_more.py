# Generated by Django 4.1 on 2022-08-23 21:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classic_tracker', '0012_alter_day_stage_alter_session_day_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.RemoveConstraint(
            model_name='stage',
            name='stage_time_usage_ratio_range',
        ),
        migrations.RemoveConstraint(
            model_name='user',
            name='user_time_usage_ratio_range',
        ),
    ]

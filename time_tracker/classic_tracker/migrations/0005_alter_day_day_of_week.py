# Generated by Django 4.1 on 2022-08-20 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classic_tracker', '0004_alter_day_day_of_week'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='day_of_week',
            field=models.SmallIntegerField(choices=[('1', 'Monday'), ('2', 'Tuesday'), ('3', 'Wednesday'), ('4', 'Thursday'), ('5', 'Friday'), ('6', 'Saturday'), ('7', 'Sunday')], editable=False),
        ),
    ]

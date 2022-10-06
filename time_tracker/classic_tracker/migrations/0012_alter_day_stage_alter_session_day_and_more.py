# Generated by Django 4.1 on 2022-08-23 18:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classic_tracker', '0011_alter_day_end_next_day_alter_session_end_next_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='stage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classic_tracker.stage'),
        ),
        migrations.AlterField(
            model_name='session',
            name='day',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classic_tracker.day'),
        ),
        migrations.AlterField(
            model_name='session',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classic_tracker.subject'),
        ),
    ]
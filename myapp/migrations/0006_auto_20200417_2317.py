# Generated by Django 2.2 on 2020-04-17 17:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_auto_20200417_2313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.User'),
        ),
    ]

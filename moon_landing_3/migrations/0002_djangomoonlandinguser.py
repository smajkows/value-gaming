# Generated by Django 3.0.6 on 2020-05-18 00:47

from django.db import migrations, models
import moon_landing_3.user


class Migration(migrations.Migration):

    dependencies = [
        ('moon_landing_3', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DjangoMoonLandingUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            bases=(models.Model, moon_landing_3.user.MoonLandingUser),
        ),
    ]

# Generated by Django 3.0.6 on 2020-05-18 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DjangoEtradeUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session', models.CharField(max_length=200)),
                ('base_url', models.CharField(max_length=200)),
            ],
        ),
    ]
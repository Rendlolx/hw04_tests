# Generated by Django 2.2.9 on 2022-08-06 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChangePasswordAfterReset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('new_pass', models.CharField(max_length=40)),
                ('new_pass_confirm', models.CharField(max_length=40)),
            ],
        ),
    ]
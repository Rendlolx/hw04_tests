# Generated by Django 2.2.9 on 2022-08-06 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20220719_1942'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post_create',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('group', models.CharField(blank=True, max_length=50)),
            ],
        ),
    ]
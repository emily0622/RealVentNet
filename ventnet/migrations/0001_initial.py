# Generated by Django 4.1.4 on 2023-03-28 03:33

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Networks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('networkname', models.CharField(max_length=50, unique=True)),
                ('desc', models.TextField(max_length=400)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('owner', models.CharField(max_length=50)),
                ('private', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['created_on'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name=django.contrib.auth.models.User)),
                ('follows', models.ManyToManyField(blank=True, related_name='followed_by', to='ventnet.profile')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NetworkMembers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.BooleanField(default=False)),
                ('verified', models.BooleanField(default=False)),
                ('invited', models.BooleanField(default=False)),
                ('accepted', models.BooleanField(default=False)),
                ('requested', models.BooleanField(default=False)),
                ('network', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='network', to='ventnet.networks')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Meep',
            fields=[
                ('title', models.CharField(max_length=50)),
                ('link', models.URLField(blank=True)),
                ('body', models.CharField(max_length=400)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('meepid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('in_network', models.BooleanField(default=False)),
                ('network', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meepnetwork', to='ventnet.networks')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='meeps', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('body', models.TextField(max_length=200)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('active', models.BooleanField(default=False)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post', to='ventnet.meep')),
            ],
            options={
                'ordering': ['created_on'],
            },
        ),
    ]

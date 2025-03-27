# Generated by Django 5.1.7 on 2025-03-25 05:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_directmessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction_type', models.CharField(choices=[('in_person', 'In Person'), ('phone_call', 'Phone Call'), ('direct_message', 'Direct Message')], max_length=20)),
                ('points', models.FloatField(help_text='Base points for this interaction')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions_sent', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions_received', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

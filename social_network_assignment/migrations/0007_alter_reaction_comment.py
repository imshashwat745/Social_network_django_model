# Generated by Django 4.2.11 on 2024-09-23 10:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social_network_assignment', '0006_alter_reaction_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reaction',
            name='comment',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reaction', to='social_network_assignment.comment'),
        ),
    ]

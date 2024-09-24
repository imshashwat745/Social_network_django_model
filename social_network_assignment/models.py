from random import choice

from aptdaemon.lock import release
from django.db import models
from django.db.models import ForeignKey, ManyToManyField, OneToOneField
from django.db.models import CharField, URLField, DateTimeField


class User(models.Model):
    name = CharField(max_length=100)
    profile_pic = URLField(null=True, blank=True, default=None)


class Post(models.Model):
    content = CharField(max_length=1000)
    posted_at = DateTimeField(auto_now_add=True)
    posted_by = ForeignKey('User', on_delete=models.CASCADE)
    group=ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name='posts'
    )


class Comment(models.Model):
    content = CharField(max_length=1000)
    commented_at = DateTimeField(auto_now_add=True)
    commented_by = ForeignKey('User', related_name='comments', on_delete=models.CASCADE, default=None)
    post = ForeignKey('Post', on_delete=models.CASCADE, related_name='comments', null=True, blank=True, default=None)
    parent_comment = ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='child_comment',
        default=None
    )


class Reaction(models.Model):
    REACTION_CHOICES = [
        ('WOW', 'WOW'),
        ('LIT', 'LIT'),
        ('LOVE', 'LOVE'),
        ('HAHA', 'HAHA'),
        ('SAD', 'SAD'),
        ('THUMBS-DOWN', 'THUMBS-DOWN'),
        ('THUMBS-UP', 'THUMBS-UP'),
        ('ANGRY', 'ANGRY'),
    ]
    reaction = CharField(
        choices=REACTION_CHOICES,
        max_length=100
    )
    reacted_at = DateTimeField(auto_now_add=True)
    reacted_by = ForeignKey('User', on_delete=models.CASCADE)
    post = ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name='reaction'
    )
    comment = ForeignKey(
        'Comment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name='reaction'
    )

    class Meta:
        unique_together = ('reacted_by', 'post', 'comment')  # Ensure one reaction per user per post/comment


class Membership(models.Model):
    REGULAR = 'regular'
    ADMIN = 'admin'

    MEMBERSHIP_TYPES = [
        (REGULAR, 'Regular'),
        (ADMIN, 'Admin'),
    ]
    membership_type = models.CharField(
        max_length=10,
        choices=MEMBERSHIP_TYPES,
        default=REGULAR
    )
    member = ForeignKey('User', on_delete=models.CASCADE)
    group = ForeignKey('Group', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('group', 'member')


class Group(models.Model):
    name = CharField(max_length=100)
    members = ManyToManyField('User', through='Membership')
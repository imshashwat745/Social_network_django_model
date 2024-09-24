from typing import List

from django.core.management.base import BaseCommand
from pyparsing import empty

from social_network_assignment.utils import delete_post


class Command(BaseCommand):
    help = 'Get all actor objects acted in given movies'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='ID of user')
        parser.add_argument('post_id', type=int, help='ID of post')
        # parser.add_argument(
        #     'movies',
        #     nargs='+',  # This allows multipparser.add_argument('post_id', type=int, help='ID of post')le arguments
        #     type=str,
        #     help='List of movie IDs'
        # )

    def handle(self, *args, **options):
        user_id = options['user_id']
        post_id = options['post_id']
        print(type(post_id))
        try:
            print(delete_post(user_id=user_id,post_id=post_id))
        except Exception as e:
            print(f"Exception: {e}")

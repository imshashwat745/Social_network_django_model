from typing import List

from django.core.management.base import BaseCommand
from pyparsing import empty

from social_network_assignment.utils import get_post


class Command(BaseCommand):
    help = 'Get all actor objects acted in given movies'

    def add_arguments(self, parser):
        parser.add_argument('post_id', type=int, help='user id')
        # parser.add_argument(
        #     'movies',
        #     nargs='+',  # This allows multiple arguments
        #     type=str,
        #     help='List of movie IDs'
        # )

    def handle(self, *args, **options):
        try:
            post_id = options['post_id']
            print(get_post(post_id=post_id))
        except Exception as e:
            print(f"Exception: {e}")

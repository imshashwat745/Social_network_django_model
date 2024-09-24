from typing import List

from django.core.management.base import BaseCommand
from pyparsing import empty

from social_network_assignment.utils import get_reaction_metrics


class Command(BaseCommand):
    help = 'Get all actor objects acted in given movies'

    def add_arguments(self, parser):
        parser.add_argument('post_id', type=int, help='ID of post')
        # parser.add_argument(
        #     'movies',
        #     nargs='+',  # This allows multiple arguments
        #     type=str,
        #     help='List of movie IDs'
        # )

    def handle(self, *args, **options):
        post_id = options['post_id']
        print(type(post_id))
        try:
            print(get_reaction_metrics(post_id))
        except Exception as e:
            print(f"Exception: {e}")

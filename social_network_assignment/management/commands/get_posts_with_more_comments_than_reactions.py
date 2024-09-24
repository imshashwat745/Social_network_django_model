from typing import List

from django.core.management.base import BaseCommand
from pyparsing import empty

from social_network_assignment.utils import get_posts_with_more_comments_than_reactions
class Command(BaseCommand):
    help = 'Get all actor objects acted in given movies'

    def add_arguments(self, parser):
        # parser.add_argument('movies', type=List[str], help='Name of the actor')
        # parser.add_argument(
        #     'movies',
        #     nargs='+',  # This allows multiple arguments
        #     type=str,
        #     help='List of movie IDs'
        # )
        pass

    def handle(self, *args, **options):
        try:
          print(get_posts_with_more_comments_than_reactions())
        except Exception as e:
            print(f"Exception: {e}")

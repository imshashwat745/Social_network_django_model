from typing import List

from django.core.management.base import BaseCommand
from pyparsing import empty

from social_network_assignment.utils import get_replies_for_comment


class Command(BaseCommand):
    help = 'Get all actor objects acted in given movies'

    def add_arguments(self, parser):
        parser.add_argument('comment_id', type=int, help='user id')
        # parser.add_argument(
        #     'movies',
        #     nargs='+',  # This allows multiple arguments
        #     type=str,
        #     help='List of movie IDs'
        # )

    def handle(self, *args, **options):
        try:
            comment_id = options['comment_id']
            print(get_replies_for_comment(comment_id=comment_id))

        except Exception as e:
            print(f"Exception: {e}")

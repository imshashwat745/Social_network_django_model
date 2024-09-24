from typing import List

from django.core.management.base import BaseCommand
from pyparsing import empty

from social_network_assignment.utils import get_silent_group_members


class Command(BaseCommand):
    help = 'Get all actor objects acted in given movies'

    def add_arguments(self, parser):
        parser.add_argument('group_id', type=int, help='group id')
        # parser.add_argument('comment_id', type=int, help='user id')
        # parser.add_argument(
        #     'member_ids',
        #     nargs='+',  # This allows multiple arguments
        #     type=int,
        #     help='List of member_ids'
        # )

    def handle(self, *args, **options):
        try:
            group_id = options['group_id']
            print(get_silent_group_members(group_id=group_id))

        except Exception as e:
            print(f"Exception: {e}")

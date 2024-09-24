from typing import List

from django.core.management.base import BaseCommand
from pyparsing import empty

from social_network_assignment.utils import create_group


class Command(BaseCommand):
    help = 'Get all actor objects acted in given movies'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='user id')
        parser.add_argument('name', type=str, help='name')
        # parser.add_argument('comment_id', type=int, help='user id')
        parser.add_argument(
            'member_ids',
            nargs='+',  # This allows multiple arguments
            type=int,
            help='List of member_ids'
        )

    def handle(self, *args, **options):
        try:
            user_id = options['user_id']
            name = options['name']
            member_ids = options['member_ids']
            # print(member_ids)
            # print(user_id)
            # print(name)
            print(create_group(user_id=user_id, name=name, member_ids=member_ids))

        except Exception as e:
            print(f"Exception: {e}")

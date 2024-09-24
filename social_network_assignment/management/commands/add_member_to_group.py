from typing import List

from django.core.management.base import BaseCommand
from pyparsing import empty

from social_network_assignment.utils import add_member_to_group


class Command(BaseCommand):
    help = 'Get all actor objects acted in given movies'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='user id')
        parser.add_argument('new_member_id', type=int, help='new member id')
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
            user_id = options['user_id']
            new_member_id = options['new_member_id']
            group_id = options['group_id']
            # print(member_ids)
            # print(user_id)
            # print(name)
            print(add_member_to_group(user_id=user_id, new_member_id=new_member_id, group_id=group_id))

        except Exception as e:
            print(f"Exception: {e}")

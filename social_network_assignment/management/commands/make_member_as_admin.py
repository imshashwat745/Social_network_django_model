from typing import List

from django.core.management.base import BaseCommand
from pyparsing import empty

from social_network_assignment.utils import make_member_as_admin


class Command(BaseCommand):
    help = 'Get all actor objects acted in given movies'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='user id')
        parser.add_argument('member_id', type=int, help='member id')
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
            member_id = options['member_id']
            group_id = options['group_id']
            # print(member_ids)
            # print(user_id)
            # print(name)
            print(make_member_as_admin(user_id=user_id, member_id=member_id, group_id=group_id))

        except Exception as e:
            print(f"Exception: {e}")

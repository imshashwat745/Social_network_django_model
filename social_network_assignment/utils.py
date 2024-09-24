from typing import List

from PIL.ImImagePlugin import number
from django.db.models import Count, Q, Prefetch, F
from django.utils import timezone
from random import choice, randint

from oauthlib.uri_validate import query
from pygments.styles.dracula import comment

from social_network_assignment.models import User, Reaction, Comment, Post, Membership, Group

from social_network_assignment.exceptions import InvalidCommentException, InvalidUserException, InvalidPostException, \
    InvalidNameOfUser, InvalidReactionTypeException, InvalidReplyContent, UserCannotDeletePostException, \
    InvalidPostContent, InvalidCommentContent, InvalidGroupNameException, InvalidMemberException, InvalidGroupException, \
    UserNotInGroupException, UserIsNotAdminException, InvalidLimitSetValueException, InvalidOffSetValueException


def create_post(user_id: int, post_content: str, group_id=None):
    if not User.objects.filter(id=user_id).exists():
        raise InvalidUserException("User does not exist")

    if not post_content.strip():
        raise InvalidPostContent("Post content should not be empty")

    group = None
    if group_id != None:
        group = Group.objects.filter(id=group_id)
        if not group.exists():
            raise InvalidGroupException("Invalid group Id")

        if not group.filter(membership__member__id=user_id).exists():
            raise UserNotInGroupException("This user is not in this group")
        group = group.first()

    post_created = Post.objects.create(content=post_content, posted_by_id=user_id, group=group)

    return post_created.id


def create_user(name: str, profile_pic: str):
    if not name.strip():
        raise InvalidNameOfUser("Name of user should not be empty")

    user_created = User.objects.create(name=name, profile_pic=profile_pic)
    return user_created.id


#
def create_comment(comment_content: str, user_id: int, post_id: int):
    if not User.objects.filter(id=user_id).exists():
        raise InvalidUserException("User does not exist")
    if not Post.objects.filter(id=post_id).exists():
        raise InvalidPostException("Post does not exist")
    if not comment_content.strip():
        raise InvalidCommentContent("Comment content should not be empty")
    comment_created = Comment.objects.create(content=comment_content, post_id=post_id, commented_by_id=user_id)
    return comment_created.id


def create_reply(reply_content: str, comment_id: int, user_id: int):
    if not User.objects.filter(id=user_id).exists():
        raise InvalidUserException("User does not exist")
    if not Comment.objects.filter(id=comment_id).exists():
        raise InvalidCommentException("Comment does not exist")
    if not reply_content.strip():
        raise InvalidReplyContent("Reply content should not be empty")
    reply_created = Comment.objects.create(content=reply_content, parent_comment_id=comment_id, commented_by_id=user_id)
    return reply_created.id


def react_to_post(user_id: int, post_id: int, reaction_type: str):
    if not User.objects.filter(id=user_id).exists():
        raise InvalidUserException("User does not exist")
    if not Post.objects.filter(id=post_id).exists():
        raise InvalidPostException("Post does not exist")
    if reaction_type not in ['WOW', 'HAHA', 'LIT', 'LOVE', 'THUMBS-UP', 'THUMBS-DOWN', 'ANGRY', 'SAD']:
        raise InvalidReactionTypeException("Invalid reaction type found")

    reaction_created = Reaction.objects.create(reaction=reaction_type, reacted_by_id=user_id, post_id=post_id)
    return reaction_created.id


def react_to_comment(user_id: int, comment_id: int, reaction_type: str):
    if not User.objects.filter(id=user_id).exists():
        raise InvalidUserException("User does not exist")
    if not Comment.objects.filter(id=comment_id).exists():
        raise InvalidCommentException("Comment does not exist")
    if reaction_type not in ['WOW', 'HAHA', 'LIT', 'LOVE', 'THUMBS-UP', 'THUMBS-DOWN', 'ANGRY', 'SAD']:
        raise InvalidReactionTypeException("Invalid reaction type found")

    reaction_created = Reaction.objects.create(reaction=reaction_type, reacted_by_id=user_id, comment_id=comment_id)
    return reaction_created.id


def get_total_number_of_reactions():
    count = Reaction.objects.count()
    return {'count': count}


def get_reaction_metrics(post_id: int):
    """
    :returns: {'LIKE':4, 'WOW':2}
    """
    if not Post.objects.filter(id=post_id).exists():
        raise InvalidPostException("Post does not exist")
    reaction_details = (Reaction.objects
                        .filter(post_id=post_id)
                        .values('reaction')  # this is group by
                        .annotate(count=Count('id'))
                        )
    return {reaction_detail['reaction']: reaction_detail['count'] for reaction_detail in reaction_details}


def delete_post(user_id, post_id):
    if not User.objects.filter(id=user_id).exists():
        raise InvalidUserException("User does not exist")

    post = Post.objects.filter(id=post_id)
    if not post.exists():
        raise InvalidPostException("This post does not exist")

    post = post.first()

    if post.posted_by_id != user_id:
        raise UserCannotDeletePostException("User cannot this post as this is not posted by this user")

    post.delete()
    # All the related comments, replies and reactions will be deleted through cascade
    print("Post deleted successfully")


def get_posts_with_more_positive_reactions():
    positive_reactions = ['THUMBS-UP', 'LIT', 'LOVE', 'HAHA', 'WOW']
    negative_reactions = ['THUMBS-DOWN', 'SAD', 'ANGRY']
    posts = (Post.objects.annotate(
        count_positive_reaction=Count('reaction', filter=Q(reaction__reaction__in=positive_reactions))
    ).filter(count_positive_reaction__gt=Count('reaction', filter=Q(reaction__reaction__in=negative_reactions))
             ).values('id')
             )

    # print(posts)
    return [post['id'] for post in posts]


def get_posts_reacted_by_user(user_id: int):
    """
    :returns: list of post ids
    """
    if not User.objects.filter(id=user_id).exists():
        raise InvalidUserException("User does not exist")

    posts = Post.objects.filter(reaction__reacted_by_id=user_id).values('id')
    return [post['id'] for post in posts]


def get_reactions_to_post(post_id: int):
    """
    :returns: [
        {"user_id": 1, "name": "iB Cricket", "profile_pic": "", "reaction": "LIKE"},
        ...
    ]
    """
    if not Post.objects.filter(id=post_id).exists():
        raise InvalidPostException("This post does not exist")

    reactions = Reaction.objects.filter(post_id=post_id
                                        ).select_related('reacted_by').values(
        'reaction',
        'reacted_by__id',
        'reacted_by__name',
        'reacted_by__profile_pic',
    )

    return [{"user_id": reaction["reacted_by__id"], "name": reaction["reacted_by__name"],
             "profile_pic": reaction["reacted_by__profile_pic"],
             "reaction": reaction["reaction"]} for reaction in reactions]


def build_and_get_commenter_data(comment):
    return {
        "user_id": comment.commented_by.id,
        "name": comment.commented_by.name,
        "profile_pic": comment.commented_by.profile_pic
    }


def build_and_get_reactions_data(reaction):
    reply_reactions = reaction.values_list('reaction', flat=True).distinct()
    reply_reaction_count = reaction.count()
    return {
        "count": reply_reaction_count,
        "type": list(reply_reactions)
    }


def build_and_get_comment_data(reply, replies_of_comment):
    reply_commenter = build_and_get_commenter_data(reply)
    reaction_data = build_and_get_reactions_data(reply.reaction)
    return {
        "comment_id": reply.id,
        "commenter": reply_commenter,
        "commented_at": reply.commented_at,
        "comment_content": reply.content,
        "reactions": reaction_data,
        "replies_count": len(replies_of_comment),
        "replies": replies_of_comment
    }


def get_replies(comment):
    replies_data = []
    replies = comment.child_comment.prefetch_related(
        'commented_by',
        'reaction')
    for reply in replies:
        replies_of_this_reply = get_replies(reply)  # Recursively get its replies
        replies_data.append(build_and_get_comment_data(reply, replies_of_this_reply))

    return replies_data


def build_and_get_user_data(queryset):
    return {
        "name": queryset.posted_by.name,
        "user_id": queryset.posted_by.id,
        "profile_pic": queryset.posted_by.profile_pic
    }

def build_and_get_group_data(queryset):
    if queryset.group is None:
        return None

    return {
        "group_id":queryset.group.id,
        "name":queryset.group.name
    }
def build_and_get_post_data(query_set):
    user_data = build_and_get_user_data(queryset=query_set)
    reaction_data = build_and_get_reactions_data(query_set.reaction)
    comments = query_set.comments.all()
    print(comments)
    comment_data = []
    if comments:
        for comment in comments:
            replies_of_this_comment = get_replies(comment)
            print("here")
            comment_data.append(build_and_get_comment_data(comment, replies_of_this_comment))

    return {
        "post_id": query_set.id,
        "posted_by": user_data,
        "posted_at": query_set.posted_at,
        "post_content": query_set.content,
        "reactions": reaction_data,
        "comments": comment_data,
        "comment_count": len(comment_data),
        "group":build_and_get_group_data(queryset=query_set)
    }


def get_post(post_id: int):
    q = (Post.objects.
    filter(id=post_id)
    .select_related(
        'posted_by'
    ).prefetch_related(
        'comments',
        'reaction'
    ))
    # print("here")
    # print(queryset)
    queryset = q.first()
    # print(queryset)
    if not queryset:
        raise InvalidPostException("This post does not exist")
    return build_and_get_post_data(queryset)


def get_user_posts(user_id: int):
    if not User.objects.filter(id=user_id).exists():
        raise InvalidUserException("This user does not exist")

    queryset = (Post.objects.
    filter(posted_by__id=user_id)
    .select_related(
        'posted_by',
        'group'
    ).prefetch_related(
        'comments',
        'reaction'
    ))

    posts = []
    for q in queryset:
        posts.append(build_and_get_post_data(q))

    return posts


def get_replies_for_comment(comment_id: int):
    """
    :returns: [{
        "comment_id": 2
        "commenter": {
            "user_id": 1,
            "name": "iB Cricket",
            "profile_pic": "https://dummy.url.com/pic.png"
        },
        "commented_at": "2019-05-21 20:22:46.810366",
        "comment_content": "Thanks...",
    }]
    """
    comment = Comment.objects.filter(id=comment_id)
    if not comment:
        raise InvalidCommentException("There is no such comment")

    comment_obj = comment.first()
    return get_replies(comment_obj)


def create_group(user_id: int, name: str, member_ids: List[int]):
    if not name.strip():
        raise InvalidGroupNameException("Group name should not be empty")
    # print(1)
    user = User.objects.filter(id=user_id)
    if not user.exists():
        raise InvalidUserException("This user does not exist")
    # print(2)
    member_objs = User.objects.filter(id__in=member_ids)
    if member_objs.count() != len(member_ids):
        #         Some member is not present
        raise InvalidMemberException("Some of the members are invalid")

    # First create group
    group = Group.objects.create(name=name)
    # print(3)
    # Create member objects and then bulk_create on db
    membership_objs = []
    membership_objs.append(Membership(member=user.first(), group=group, membership_type=Membership.ADMIN))
    for member_obj in member_objs:
        membership_objs.append(Membership(member=member_obj, group=group, membership_type=Membership.REGULAR))
    # print(4)
    Membership.objects.bulk_create(membership_objs)

    return group.id


def add_member_to_group(user_id: int, new_member_id: int, group_id: int):
    user = User.objects.filter(id=user_id)
    if not user.exists():
        raise InvalidUserException("This user is invalid")
    new_member = User.objects.filter(id=new_member_id)

    if not new_member.exists():
        raise InvalidUserException("This new_member is invalid")

    group = Group.objects.filter(id=group_id)
    if not group.exists():
        raise InvalidGroupException("This group does not exist")

    membership = Membership.objects.filter(group=group.first()).filter(member=user.first())
    if not membership.exists():
        raise UserNotInGroupException("User is not i group")

    if membership.first().membership_type != Membership.ADMIN:
        raise UserIsNotAdminException("User is not an admin")

    if not Membership.objects.filter(group=group.first()).filter(member=new_member.first()).exists():
        Membership.objects.create(group=group.first(), member=new_member.first(), membership_type=Membership.REGULAR)

    print("Added successfully")


def remove_member_from_group(user_id: int, member_id: int, group_id: int):
    user = User.objects.filter(id=user_id)
    if not user.exists():
        raise InvalidUserException("This user is invalid")
    member = User.objects.filter(id=member_id)

    if not member.exists():
        raise InvalidUserException("This member is invalid")

    group = Group.objects.filter(id=group_id)
    if not group.exists():
        raise InvalidGroupException("This group does not exist")

    membership_user = Membership.objects.filter(group=group.first()).filter(member=user.first())
    if not membership_user.exists():
        raise UserNotInGroupException("User is not i group")

    if membership_user.first().membership_type != Membership.ADMIN:
        raise UserIsNotAdminException("User is not an admin")

    membership_member = Membership.objects.filter(group=group.first()).filter(member=member.first())
    if not membership_member.exists():
        raise UserNotInGroupException("Member is not in group")

    membership_member.first().delete()
    print("Deleted Successfully")


def make_member_as_admin(user_id: int, member_id: int, group_id: int):
    user = User.objects.filter(id=user_id)
    if not user.exists():
        raise InvalidUserException("This user is invalid")
    member = User.objects.filter(id=member_id)

    if not member.exists():
        raise InvalidUserException("This member is invalid")

    group = Group.objects.filter(id=group_id)
    if not group.exists():
        raise InvalidGroupException("This group does not exist")

    membership_user = Membership.objects.filter(group=group.first()).filter(member=user.first())
    if not membership_user.exists():
        raise UserNotInGroupException("User is not i group")

    if membership_user.first().membership_type != Membership.ADMIN:
        raise UserIsNotAdminException("User is not an admin")

    membership_member = Membership.objects.filter(group=group.first()).filter(member=member.first())
    if not membership_member.exists():
        raise UserNotInGroupException("Member is not in group")

    membership_member.update(membership_type=Membership.ADMIN)
    print("Updated Successfully")


def get_group_feed(user_id: int, group_id: int, offset: int, limit: int):
    if limit <= 0:
        raise InvalidLimitSetValueException("Invalid limit value")

    if offset < 0:
        raise InvalidOffSetValueException("Invalid offset value")

    user = User.objects.filter(id=user_id)
    if not user.exists():
        raise InvalidUserException("This user is invalid")

    group = Group.objects.filter(id=group_id)
    if not group.exists():
        raise InvalidGroupException("This group does not exist")

    membership_user = Membership.objects.filter(group=group.first()).filter(member=user.first())
    if not membership_user.exists():
        raise UserNotInGroupException("User is not in group")

    queryset = (
        Post.objects
        .filter(group_id=group_id)
        .select_related('posted_by','group')
        .prefetch_related('comments', 'reaction')
        .order_by('-posted_at')[offset:offset + limit]  # Apply offset and limit
    )

    posts = []
    for q in queryset:
        posts.append(build_and_get_post_data(q))

    return posts


def get_posts_with_more_comments_than_reactions():
    """
    :returns: list of post_ids
    """
    posts = Post.objects.annotate(
        number_of_comments=Count('comments', distinct=True),
        number_of_reactions=Count('reaction', distinct=True)
    ).filter(number_of_comments__gt=F('number_of_reactions'))

    return [post.id for post in posts]

def get_silent_group_members(group_id):
    """
    """

    group = Group.objects.filter(id=group_id)
    if not group.exists():
        raise InvalidGroupException("This group does not exist")

    users=User.objects.filter(membership__group_id=group_id).exclude(
        Q(post__group_id=group_id)
    )

    return [user.id for user in users]

def populate_db():
    # Create sample users
    user1_id = create_user(name='Alice', profile_pic='https://example.com/alice.jpg')
    user2_id = create_user(name='Bob', profile_pic='https://example.com/bob.jpg')
    user3_id = create_user(name='Charlie', profile_pic='https://example.com/charlie.jpg')
    user4_id = create_user(name='David', profile_pic='https://example.com/david.jpg')
    user5_id = create_user(name='Eve', profile_pic='https://example.com/eve.jpg')  # Silent member
    user6_id = create_user(name='Frank', profile_pic='https://example.com/frank.jpg')  # Silent member

    # Create a sample group and add members
    group_id = create_group(user_id=user1_id, name='Friends', member_ids=[user2_id, user3_id, user4_id, user5_id, user6_id])

    # Create sample posts in the group
    post1_id = create_post(user_id=user1_id, post_content="Alice's first post in Friends", group_id=group_id)
    post2_id = create_post(user_id=user2_id, post_content="Bob's first post in Friends", group_id=group_id)
    post3_id = create_post(user_id=user3_id, post_content="Charlie's first post in Friends", group_id=group_id)
    # Note: user5_id and user6_id (Eve and Frank) are silent members who haven't posted

    # Create sample posts outside the group
    post4_id = create_post(user_id=user1_id, post_content="Alice's public post")
    post5_id = create_post(user_id=user4_id, post_content="David's public post")

    # Create sample comments on the posts
    # Post 1 has 3 comments
    comment1_id = create_comment(comment_content="Bob commenting on Alice's post", user_id=user2_id, post_id=post1_id)
    comment2_id = create_comment(comment_content="Charlie commenting on Alice's post", user_id=user3_id, post_id=post1_id)
    comment3_id = create_comment(comment_content="David commenting on Alice's post", user_id=user4_id, post_id=post1_id)

    # Post 2 has 1 comment
    comment4_id = create_comment(comment_content="Alice commenting on Bob's post", user_id=user1_id, post_id=post2_id)

    # Post 3 has 2 comments
    comment5_id = create_comment(comment_content="Bob commenting on Charlie's post", user_id=user2_id, post_id=post3_id)
    comment6_id = create_comment(comment_content="Alice commenting on Charlie's post", user_id=user1_id, post_id=post3_id)

    # Post 4 has 1 comment (outside group)
    comment7_id = create_comment(comment_content="Bob commenting on Alice's public post", user_id=user2_id, post_id=post4_id)

    # Create nested comments (replies)
    # Replies to comment1_id (on Post 1)
    reply1_id = create_reply(reply_content="Alice replying to Bob's comment", comment_id=comment1_id, user_id=user1_id)
    reply2_id = create_reply(reply_content="Charlie replying to Bob's comment", comment_id=comment1_id, user_id=user3_id)

    # Replies to comment5_id (on Post 3)
    reply3_id = create_reply(reply_content="Charlie replying to Bob's comment", comment_id=comment5_id, user_id=user3_id)

    # Add reactions to posts
    # Post 1 has 1 reaction
    react_to_post(user_id=user2_id, post_id=post1_id, reaction_type='WOW')  # Bob reacts to Alice's post

    # Post 2 has 3 reactions
    react_to_post(user_id=user1_id, post_id=post2_id, reaction_type='LOVE')  # Alice reacts to Bob's post
    react_to_post(user_id=user3_id, post_id=post2_id, reaction_type='HAHA')  # Charlie reacts to Bob's post
    react_to_post(user_id=user4_id, post_id=post2_id, reaction_type='THUMBS-UP')  # David reacts to Bob's post

    # Post 3 has 1 reaction
    react_to_post(user_id=user4_id, post_id=post3_id, reaction_type='SAD')  # David reacts to Charlie's post

    # Post 4 has 2 reactions
    react_to_post(user_id=user2_id, post_id=post4_id, reaction_type='LOVE')  # Bob reacts to Alice's public post
    react_to_post(user_id=user3_id, post_id=post4_id, reaction_type='THUMBS-UP')  # Charlie reacts to Alice's public post

    # Add reactions to comments
    react_to_comment(user_id=user3_id, comment_id=comment4_id, reaction_type='HAHA')  # Charlie reacts to Alice's comment
    react_to_comment(user_id=user4_id, comment_id=comment2_id, reaction_type='ANGRY')  # David reacts to Charlie's comment
    react_to_comment(user_id=user1_id, comment_id=comment5_id, reaction_type='LOVE')  # Alice reacts to Bob's comment

    print("Database populated successfully with sample data.")

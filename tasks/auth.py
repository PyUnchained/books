# from django.contrib.auth import get_user_model

# from celery import shared_task

# from books.utils.auth import register_new_account

# User = get_user_model()

# @shared_task
# def create_user_account(user_pk):
#     u = User.objects.get(pk = user_pk)
#     register_new_account(user = u, name = u.username)
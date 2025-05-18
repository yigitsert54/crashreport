from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_save
from .models import Account, WorkshopData
import os


# Signals info:
# sender = The Model that triggers the action
# instance = the instance of the model (e.g. instance="Yigit Sert" from model="Account")
# created = True or False (new Instance was created or just saved/modified/changed)


# Create account when user is created
@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    """
    Create a new account everytime a new user is created.
    """

    # Check whether a new user has just been added
    if created:
        # Extract user
        user = instance

        # Create new Account
        Account.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.username
        )


# Update user when account is updated
@receiver(post_save, sender=Account)
def update_user(sender, instance, created, **kwargs):
    account = instance
    user = account.user

    if created == False:
        user.first_name = account.first_name
        user.last_name = account.last_name
        user.email = account.email
        user.username = account.email
        user.save()


# Delete User when Account is deleted
@receiver(post_delete, sender=Account)
def delete_user(sender, instance, **kwargs):
    """
    Delete connected user when account is deleted! - The other way around is handled in the model 'on_delete=models.CASCADE'
    """

    # Extract connected user
    user = instance.user
    user.delete()


# Delete verification document from media directory when verification document is changed or deleted
@receiver(pre_save, sender=WorkshopData)
def delete_document(sender, instance, **kwargs):
    """
    Deletes verification document from media directory when it is updated or deleted
    """

    # Check if instance already exists (make sure it is not a new object)
    if instance.id and WorkshopData.objects.filter(id=instance.id).exists():

        # Extract old (pre save) settings instance
        pre_save_data = sender.objects.get(id=instance.id)

        # Extract updated settings instance
        updated_data = instance

        # If pre save and updated documents don't match
        if pre_save_data.verification_document and pre_save_data.verification_document != updated_data.verification_document:

            # Delete if path exists
            if os.path.isfile(pre_save_data.verification_document.path):
                os.remove(pre_save_data.verification_document.path)

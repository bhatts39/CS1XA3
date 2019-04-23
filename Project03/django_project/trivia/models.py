from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserInfo(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                primary_key=True,
                                related_name='info')
    points = models.IntegerField(default=0)

class TriviaQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.TextField()
    question = models.TextField()
    choice1 = models.TextField()
    choice2 = models.TextField()
    choice3 = models.TextField()
    choice4 = models.TextField()
    correctChoice = models.IntegerField()

class Game(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.IntegerField(default=0)
    p1 = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='p1')
    p2 = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='p2',
                                default=None,
                                null=True
                                )
    p1lives = models.IntegerField(default=2)
    p2lives = models.IntegerField(default=2)
    p1choice = models.IntegerField(default=0)
    p2choice = models.IntegerField(default=0)
    questionNum = models.IntegerField(default=0)
    question = models.ForeignKey(TriviaQuestion,
                                on_delete=models.CASCADE,
                                related_name='triviaQuestion')
    timeUpdated = models.DateTimeField(auto_now=True)
    winner = models.IntegerField(default=0)



@receiver(post_save, sender=User)
def create_user_info(sender, instance, created, **kwargs):
    if created:
        UserInfo.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_info(sender, instance, **kwargs):
    instance.info.save()

  

                            

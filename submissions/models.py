from django.db import models

# Create your models here.
class Contest(models.Model):
    contest_id = models.IntegerField(unique=True,primary_key=True)
    name = models.CharField(max_length=200)
    fetched = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class User(models.Model):
    handle = models.CharField(max_length=100)
    rank = models.IntegerField()
    contest = models.ForeignKey(Contest,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('handle','contest')

    def __str__(self):
        return f"{self.handle} (Rank: {self.rank})"
    
class Submission(models.Model):
    submission_id = models.BigIntegerField(unique=True,primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    problem_index = models.CharField(max_length=1)
    problem_name = models.CharField(max_length=200)
    programming_language = models.CharField(max_length=50)
    verdict = models.CharField(max_length=50,default='Pending')
    code = models.TextField(null=True,blank=True)
    fetched = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.handle} - {self.problem_index} - {self.submission_id}"

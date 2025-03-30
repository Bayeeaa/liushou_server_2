from django.db import models

class User(models.Model):
    nickname = models.CharField(max_length=100,unique=True)
    name = models.CharField(max_length=100)
    identity = models.CharField(max_length=50)
    sex = models.CharField(max_length=10)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class ProjectOverview(models.Model):
    title = models.CharField(max_length=200)  # 文章标题
    content = models.TextField()  # 文章内容
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 文章作者，关联到 User 表

    def __str__(self):
        return self.title
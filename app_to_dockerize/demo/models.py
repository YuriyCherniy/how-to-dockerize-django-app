from django.db import models


class DemoObjectModel(models.Model):
    demo_entry = models.CharField(max_length=50, verbose_name='Добавить запись')

    def __str__(self):
        return self.demo_entry


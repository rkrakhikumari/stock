from django.db import models

class SearchHistory(models.Model):
    search_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Search Count: {self.search_count}"


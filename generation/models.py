from django.db import models


class GenerationTask(models.Model):
    STATUS = (
        ('QUEUED',  'Queued'),
        ('STARTED', 'Started'),
        ('READY',   'Ready'),
        ('ERROR',   'Error'),
    )
    prompt = models.TextField()
    tg_chat_id = models.BigIntegerField()
    status = models.CharField(max_length=10, choices=STATUS, default='QUEUED')
    image = models.ImageField(upload_to='fooocus/', null=True, blank=True)
    qty = models.PositiveSmallIntegerField(default=1)
    style_selections = models.JSONField(default=list, blank=True)
    base_model_name = models.CharField(max_length=200, blank=True)
    performance_selection = models.CharField(max_length=50, default="Speed", blank=True)
    aspect_ratios_selection = models.CharField(max_length=20, default="1152*896", blank=True)
    save_extension = models.CharField(max_length=10, default="png", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class GeneratedImage(models.Model):
    task = models.ForeignKey(
        GenerationTask,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="fooocus/")
    index = models.PositiveSmallIntegerField()


class DailyPrompt(models.Model):
    date = models.DateField(unique=True)
    emoji = models.CharField(max_length=4, default="💡")
    prompt = models.TextField()

    class Meta:
        ordering = ["-date"]
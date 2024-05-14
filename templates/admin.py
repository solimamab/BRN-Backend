from django.contrib import admin
from .models import GlasserRegion, Paper, Experiment, Measurement, ColeNetwork

# Register your models here.
admin.site.register(GlasserRegion)
admin.site.register(Paper)
admin.site.register(Experiment)
admin.site.register(Measurement)
admin.site.register(ColeNetwork)
from parties.models import Party
from rates.models import RateGroup
from materials.models import Material

for i in range(10):
    rate_group = RateGroup.objects.create(name="Group 1")
    Party.objects.create(name="P {}".format(i), rate_group=rate_group, phone=str(i), whatsapp=str(i))
    Material.objects.create(name="Material {}".format(i), code="M {}".format(i))

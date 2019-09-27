from parties.models import Party
from rates.models import RateGroup
from materials.models import Material


for i in range(1, 4):
    rate_group = RateGroup.objects.create(name="Group {}".format(i))

rate_group = RateGroup.objects.get(name="Group 1")

for i in range(1, 10):
    Party.objects.create(name="P {}".format(i), rate_group=rate_group, phone=str(i), whatsapp=str(i))
    Material.objects.create(name="Material {}".format(i), code="M {}".format(i))

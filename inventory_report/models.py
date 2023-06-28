from django.db import models


class InventoryReport(models.Model):
    date = models.DateField()
    partner = models.ForeignKey("partner.Partner", on_delete=models.CASCADE)

    def __str__(self):
        return "{} inventory report from {}".format(self.partner, self.date)


class InventoryReportLocation(models.Model):
    name = models.CharField(max_length=200)
    partner = models.ForeignKey("partner.Partner", on_delete=models.CharField)

    def __str__(self):
        return self.name


class InventoryReportLine(models.Model):
    report = models.ForeignKey(InventoryReport, on_delete=models.CASCADE, related_name='report_lines')
    location = models.ForeignKey(InventoryReportLocation, on_delete=models.SET_NULL, null=True)
    barcode = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.location:

            return "{} in {}, scanned at {}".format(self.barcode, self.location, self.timestamp)
        else:
            return "{}, scanned at {}".format(self.barcode, self.timestamp)

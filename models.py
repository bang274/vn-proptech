from django.db import models

class Property(models.Model):
    # This is how we made our money: structured data.
    title = models.CharField(max_length=200)
    price_in_billions = models.DecimalField(max_digits=10, decimal_places=2) 
    location_district = models.CharField(max_length=100) # e.g., "District 1", "Thao Dien"
    area_sqm = models.IntegerField()
    
    # The "Secret Sauce" fields (Things regular agents miss)
    alley_width_meters = models.FloatField(help_text="Width of the ngo/hem in front of house")
    is_legal_clear = models.BooleanField(default=False, help_text="Is the Red Book (So Do) ready?")
    
    def __str__(self):
        return f"{self.title} - {self.price_in_billions} Billion VND"
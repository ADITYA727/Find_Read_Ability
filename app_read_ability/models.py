from django.db import models

# Create your models here.
class StoreData(models.Model):  
    file_names = models.CharField(max_length=80) 
    tl_twts = models.CharField(max_length=20)  
    tl_sents = models.CharField(max_length=20)  
    tl_wrds = models.CharField(max_length=20)  
    tl_sylbs = models.CharField(max_length=20) 
    median = models.CharField(max_length=20, name='median')
    read_scores = models.CharField(max_length=20)

    def __str__(self):
    	return self.file_names


class DataView(models.Model):
	file_id = models.ForeignKey(StoreData, default=None ,on_delete=models.CASCADE)
	file_name = models.CharField(max_length=80)
	tl_twt = models.CharField(max_length=20)
	tl_wrd = models.CharField(max_length=20)
	tl_sylb = models.CharField(max_length=20)
	median = models.CharField(max_length=20)
	read_score = models.CharField(max_length=20)
	 

        
    
  
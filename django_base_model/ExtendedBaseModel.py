'''
Created on Jun 15, 2012

@author: rogelio
'''


from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError    
from ExtendedBaseModelManager import ExtendedBaseModelManager
    
    
from django_extensions.db.models import TimeStampedModel

class ExtendedBaseModel(models.Model):
    '''This model is an extension of models.Model aimed to provide additional functionality by 
    using the ExtendedBaseModelManager.
    
    Additionally, all subclasses inherit the deleted BooleanField which aims to provide soft
    delete functionality. 
    
    This means that any call to delete() will only flag the object as deleted=True but the object
    won't be deleted from the database. The default query set will ignore all objects flagged as 
    deleted. See get_query_set and pure_query set in ExtendedBaseModelManager.
    
    If you need to actually delete the information from the database, call hard_delete()
    '''
    
    deleted = models.BooleanField(null=False, default=False)
        
    # The objects object
    objects = ExtendedBaseModelManager()
    
    class Meta:
        abstract = True
                
    def soft_delete(self):
        '''Soft delete sets the deleted flag to true instead of deleting from the db'''
        self.deleted = True
        self.save()
                
    def hard_delete(self):
        '''Hard delete actually deletes the record in the db'''
        super(ExtendedBaseModel, self).delete()
    
    def delete(self):
        '''Delete is overriden. This performs a soft delete'''
        self.soft_delete()
        
    def save(self, *args, **kwargs):
        '''Saves the object to the database.
        
        Additional steps are necessary to support soft deletion.
        
        Since soft-deleted persist in the database, when an INSERT is issued the
        result is an IntegrityError due to a duplicated primary key.
        
        The way this is resolved is by putting the deleted flag to False and 
        updating the existing record with the new information.
        '''
        try:
            super(ExtendedBaseModel, self).save(*args, **kwargs)
        except IntegrityError, e:
            # Undetected repetitions can occur if the object was soft deleted
            # since the query set used is made to not return soft deleted items
            # See get_query_set in the objects manager
            reason = e.args[1].lower()
            if not ('primary' in reason or 
                    'unique' in reason):
                raise
            
            kwargs['force_update'] = True
            kwargs['force_insert'] = False
            return self.save(*args, **kwargs)
        
class TimeStampedExtendedBaseModel(ExtendedBaseModel, TimeStampedModel):
    
    # The objects object
    objects = ExtendedBaseModelManager()    
    
    class Meta:
        abstract = True
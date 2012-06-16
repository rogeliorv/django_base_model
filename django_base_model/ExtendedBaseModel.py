'''
Created on Jun 15, 2012

@author: rogelio
'''


from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError    

from ExtendedBaseModelManager import ExtendedBaseModelManager
    

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
        When the user wants to create an object and it clashes a soft_deleted object we
        proceed to un-delete the object and update it with the new information provided by the user.
        '''
        
        try:
            super(ExtendedBaseModel, self).save(*args, **kwargs)
        except IntegrityError, e:
            # Undetected repetitions can occur if the object was soft deleted
            # since the query set used is made to not return soft deleted items
            # See get_query_set in the objects manager
            reason = e.args[1].lower()
            if 'primary' in reason or 'unique' in reason:
                try:
                    # Try to get the previous record if there is any
                    query_set = self.__class__.objects.pure_query_set()
                    previous = query_set.get(pk = self.pk)
                    if previous.deleted:
                        kwargs['force_update'] = True
                        kwargs['force_insert'] = False
                        return self.save(*args, **kwargs)
                    raise
                except ObjectDoesNotExist:
                    raise
            else:
                raise

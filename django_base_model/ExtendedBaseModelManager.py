'''
Created on Jun 15, 2012

@author: rogelio
'''


from django.db import models
from django.db.models import sql
from django.db import connection

from django.core.exceptions import ObjectDoesNotExist


class ExtendedBaseModelManager(models.Manager):
    '''This class works as a manager for the ExtendedBaseModel.
    
    ExtendedBaseModel overrides the default 'objects' to use this class instead.
    This class aims to provide additional functionality to models.Manager (the default 
    objects class), maintaining compatibility and all the functions of the base manager.
    
    If you want to use a different manager just change the objects variable in your model.
    
    Additional functions include:
        get_or_none
        bulk_insert_ignore
        
        
    By default the query_set returned by this class ignores soft_deleted instances (deleted=True),
    if you need to work on those instances too, you can use the pure_query_set.
    '''
        
    def __init__(self):
        '''Initialize the manager'''
        super(ExtendedBaseModelManager, self).__init__()
            
    def get_or_none(self, *args, **kwargs):
        '''Tries to get an object in the database if it doesn't exist returns None.
        Receives the sames arguments as the default get
        '''
        try:
            return super(ExtendedBaseModelManager, self).get(*args, **kwargs)
        except ObjectDoesNotExist:
            return None
                
    def pure_query_set(self):
        '''A normal query set that does not avoid soft deleted values'''
        return super(ExtendedBaseModelManager, self).get_query_set()
        
    def bulk_insert_ignore(self, objs):
        '''Given an iterable of any model instance, uses the SQL cursor to apply a bunch of
        INSERT IGNORE statements in one go.
        '''
        if not objs: return
        # Get the fields from the model
        fields = self.model._meta.local_fields
        # Make an insert query
        query = sql.InsertQuery(self.model)
        # Given the objects and the fields, prepare the query 
        query.insert_values(fields, objs, raw=False)
        compiled = query.get_compiler(self.db)
        compiled.return_id = False
        # Get the raw query and the values as a tuple
        q, values = compiled.as_sql()[0]
        # Put the insert ignore statement
        q = q.replace('INSERT', 'INSERT IGNORE')
        # Get the cursor and execute
        cursor = connection.cursor()
        cursor.execute(q, values)
        return cursor
        
    def get_query_set(self):
        '''Returns the query set, which avoids returning soft deleted values. 
        If you want a normal query set call pure_query_set()'''
        return self.pure_query_set().filter(deleted=False)
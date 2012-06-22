'''
Created on Jun 15, 2012

@author: rogelio
'''

from django.db.models.query import QuerySet

class CaseInsensitiveQuerySet(QuerySet):
    '''This QuerySet is not used by default in the ExtendedBaseModel, but is another utility
    query set which provides case insensitive searches.
    
    This Query set is used to replace the normal query set when case insensitivity is needed in queries.
    
    For example, in a tag model we usually do not care about case, thus it is necessary to provide
    case insensitivity without the need remember to add __iexact in every query.
    
    To use this class you need to declare the get_query_set function in your model manager. For example:

    class ExampleManager(models.Manager)
        
        def get_query_set(self):
            return CaseInsensitiveQuerySet(self.model)


    class ExampleModel(models.Model):
        text = CharField(max_length=100)
        objects = ExampleManager()
    '''
    
    def __init__(self, *args, **kwargs):
        model = (args and args[0]) or kwargs.get('model', None)
        if model:
            manager = model.objects
            self.base_query_set = super(manager.__class__, manager).get_query_set()
        
        super(CaseInsensitiveQuerySet, self).__init__(*args, **kwargs)
    
    def _filter_or_exclude(self, mapper, *args, **kwargs):
        '''Executes filter or exclusion in a case insensitive fashion'''
        # 'name' is a field in your Model whose lookups you want case-insensitive by default
        if 'name' in kwargs:
            kwargs['name__iexact'] = kwargs['name']
            del kwargs['name']
        return  (self.base_query_set._filter_or_exclude(mapper, *args, **kwargs) & 
                 super(CaseInsensitiveQuerySet, self)._filter_or_exclude(mapper, *args, **kwargs))        

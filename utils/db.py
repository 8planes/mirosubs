from django.db import connections

def _gen_lock_statement(connection, table):
    engine_name = connection.settings_dict["ENGINE"].split(".")[-1]
    if engine_name == 'mysql':
        return "LOCK TABLES `%s` WRITE;"  % table
    return ""

def _gen_unlock(connection):
    engine_name = connection.settings_dict["ENGINE"].split(".")[-1]
    if engine_name == 'mysql':
        return "UNLOCK TABLES;"
    return ""

def require_lock(func):
    # FIXME: fetach the right connection for this model
    connection = connections['default']
    def _lock(*args,**kws):
        self = args[0]
        table = self.model._meta.db_table

        #lock tables
        cursor = connection.cursor()
        cursor.execute(_gen_lock_statement(connection, table))
        try:
            result = func(*args,**kws)
        except:
            raise 
        else:
            return result
        finally:
            #unlock tables
            cursor.execute(_gen_unlock(connection))
            if cursor:cursor.close()
    return _lock                        

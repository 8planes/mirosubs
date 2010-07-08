import sys, os
from django.core.management.base import NoArgsCommand
from django.template import loader, Context
from django.conf import settings
from haystack.constants import DEFAULT_OPERATOR

SOLR_ROOT = settings.SOLR_ROOT


class Command(NoArgsCommand):
    help = "Generates a Solr schema and applies to SOLR_ROOT instance of solr."
    
    def handle_noargs(self, **options):
        """Generates a Solr schema that reflects the indexes."""
        # Cause the default site to load.
        from django.conf import settings
        from haystack import backend, site
        
        default_operator = getattr(settings, 'HAYSTACK_DEFAULT_OPERATOR', 
                                   DEFAULT_OPERATOR)
        content_field_name, fields = backend.SearchBackend().build_schema(
            site.all_searchfields())
        
        t = loader.get_template('search/configuration/solr.xml')
        c = Context({
            'content_field_name': content_field_name,
            'fields': fields,
            'default_operator': default_operator,
        })
        schema_xml = t.render(c)
        schema_path = os.path.join(SOLR_ROOT, 'solr/conf/schema.xml')
        file = open(schema_path, 'w')
        file.write(schema_xml)
        file.close()
        sys.stderr.write("\n")
        sys.stderr.write("Saved to %s\n" % schema_path)
        sys.stderr.write("You may need to reindex your data\n")
        sys.stderr.write("--------------------------------------------------------------------------------------------\n")
        sys.stderr.write("\n")

from django.core.management.base import BaseCommand, CommandError
from listener.models import *
from listener.loader import *

class Command(BaseCommand):
    args = '<GoogleReader|Facebook>'
    help = 'Invokes the loader for a specific type'

    def handle(self, *args, **options):
        if not args:
            raise CommandError("Please enter the name of a loader")

        for data_source_type in args:
            try:
                class_name = "%sLoader()" % data_source_type
                instance = eval(class_name)
                for i in range(1,30):
                    instance.load()
            except NameError:
                raise CommandError('Loader "%sLoader" does not exist' % data_source_type)


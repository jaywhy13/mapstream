from django.core.management.base import BaseCommand, CommandError
from listener.models import *
from listener.loader import *
from sherlock.search import *

class Command(BaseCommand):
    args = ''
    help = 'Invokes the smart search engine'

    def handle(self, *args, **options):
        agent = BasicAgent()
        algorithm = GazetteerSearchAlgorithm()
        agent.search(algorithm=algorithm)
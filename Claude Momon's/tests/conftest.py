import os
import sys

# Permet d'importer les modules du projet (laminate, polar...) depuis le dossier tests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

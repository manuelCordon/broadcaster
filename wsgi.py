import os,sys
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))
from im.core.config import configure, conf, configs
configure(set_project_path=os.path.dirname(os.path.abspath(__file__)) + '/')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "im.core.settings")
os.environ["HOME"] = os.path.dirname(os.path.abspath(__file__)) + '/'

reload(sys)
sys.setdefaultencoding("utf8")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

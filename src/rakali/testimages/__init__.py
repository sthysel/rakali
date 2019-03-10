from pkg_resources import resource_filename
from ..img import Image

print(resource_filename(__name__, 'rakali.jpg'))
rakali = Image.from_file(resource_filename(__name__, 'rakali.jpg'))
orb_spider = Image.from_file(resource_filename(__name__, 'orb-spider.jpg'))

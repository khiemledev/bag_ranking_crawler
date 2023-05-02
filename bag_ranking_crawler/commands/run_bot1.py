from scrapy.commands import ScrapyCommand
from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings


class Command(ScrapyCommand):
    requires_project = True

    def syntax(self):
        return ' [options]'

    def short_desc(self):
        return 'Run bot 1'

    def run(self, args, opts):
        spider_list = self.crawler_process.spiders.list()
        spider_list = [name for name in spider_list if name.endswith('_link')]
        for spider_name in spider_list:
            print("Running spider %s" % (spider_name))
            spider = self.crawler_process.create_crawler(spider_name)
            self.crawler_process.crawl(spider)
        self.crawler_process.start()

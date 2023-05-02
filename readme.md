# Bag ranking crawler

## Quick start

Please ensure these env variables:

```bash
export RABBITMQ_HOST=
export RABBITMQ_USERNAME=
export RABBITMQ_PASSWORD=
export RABBITMQ_EXCHANGE=bag_ranking_crawl_link
export RABBITMQ_QUEUE=bag_ranking_crawl_link

export MONGO_CONNECTION_STRING=mongodb://<user>:<password>@<host>:<port>
export MONGO_DBNAME=kl_bag_ranking
export MONGO_COLLECTION=bag_ranking

```

Install dependencies:

```bash
pip3 install -r requirements.txt
```

Run bot 1 to get links:

```bash
scrapy run_bot1
```

Run bot 2 to get links:

```bash
scrapy run_bot1
```

**Note: run bot1 before bot2**

Run bot 3:

```bash
scrapy crawl bot3
```

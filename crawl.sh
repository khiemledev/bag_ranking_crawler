name="$1"
if [ -z "$name" ]; then
    echo "Usage: $0 <name>"
    exit 1
fi

mkdir -p log
mkdir -p output

scrapy crawl "$name" -o "output/$name.json" -L INFO --logfile "log/$name.log"

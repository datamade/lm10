export PGPASSWORD=postgres

all: extract_json

clean:
	rm -f final/*

.INTERMEDIATE: response_files.txt

sample.txt: 
	ls -d raw/* | shuf | head -100 > $@

extract_json: sample.txt
	python scripts/process_pdfs.py $^

sample.geojson: response_files.txt 
	python scripts/build_db.py $^ > $@

db: sample.geojson
	ogr2ogr -f "PostgreSQL" PG:"dbname=lm10 user=postgres password=postgres host=lm10-db" $< -nln blocks -append
	touch db

response_files.txt:
	ls -d textract_responses/* > $@

extracted.csv: db 
	psql -d lm10 -h lm10-db -U postgres -f scripts/extract_11b.sql > $@

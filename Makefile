all: extract_json

clean:
	rm -f final/*

sample.txt: 
	ls -d raw/* | shuf | head -100 > $@

extract_json: sample.txt
	python scripts/process_pdfs.py $^



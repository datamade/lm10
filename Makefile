all: final/LM-10_E5044_12_31_2009_425049.json

clean:
	rm -f final/*

sample.txt: 
	ls -d raw/* | shuf | head -100 > $@

extract_json: sample.txt
	python scripts/process_pdfs.py $^



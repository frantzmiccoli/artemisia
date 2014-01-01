all: info

info:
	echo 'to run something type "make demo"'

demo: demo_plot demo_export

demo_plot:
	python ../src/artemisia.py plot -l mypackage.mysubpackage.mysubsubpackage -i data -y "AVG(normalized_temperature)" -x version_number -c room

demo_export:
	python ../src/artemisia.py export -l mypackage.mysubpackage.mysubsubpackage -i data -c "normalized_temperature" -c version_number -c room -o output.csv
	python ../src/artemisia.py export -l mypackage.mysubpackage.mysubsubpackage -i data -c "normalized_temperature" -c version_number -c room -o output.arff -t arff

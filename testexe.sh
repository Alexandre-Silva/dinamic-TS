#! /bin/sh

for i in $( seq 0 20 ); do
	echo "test";
	sleep 2;
done

echo "ERROR: testexe.sh was not terminated"

exit 0

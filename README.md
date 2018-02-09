# trips
processing TRIPS

Usage:
Step 1:
python parse_trips_xml.py --path PATH-TO-DIRECTORY-WITH-TRIPS-XMLs

The clean XMLs corresponding to the original TRIPS XMLs will be created in the same directory containing the original XMLs. If any of the original XML files did not contain parses, their names will be added to .err file created in the current directory with current time and.err extension in its name.

Step 2:
python convert_cleaned_xmls_to_refinedxmls.py --path PATH-TO-DIRECTORY-WITH-TRIPS-XMLs

This will take the original XMLs as well as the clean XMLs produced in step 1 and refine the cleaned XMLs further.

TO DO: The changes in step 2 should be made while producing the clean XMLs in step 1 itself to make it more efficient. 

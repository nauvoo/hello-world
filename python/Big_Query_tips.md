# Operations in Big Query

Using arrays for faster and more reliable data processing that can easily scale up (especially for funnel composition)

Google Cloud documentation: https://cloud.google.com/bigquery/docs/reference/standard-sql/arrays#scanning-for-values-that-satisfy-a-condition

Array functions: https://cloud.google.com/bigquery/docs/reference/standard-sql/array_functions

ARRAY_CONCAT_AGG (ARRAY (SELECT as struct field1, field2, field3 FROM UNNEST (hits) ORDER BY sequence) ORDER BY sequence/starttime ASC ) as userHits
* allows to aggregate a bunch of fields into a single object that later can be expanded or deconstructed


WITH OFFSET addition to ARRAY function allows us to create 0 position index for each element in an array. 

    ARRAY (( SELECT AS STRUCT index+1 as sequencenumber,
      field1, field2 FROM UNNEST (userHits) WITH OFFSET AS index 

### To create funnel with arrays

When array is built (construct array with array func and "select as STRUCT"), one can perform a left self join to outline the steps in the funnel, using LIMIT 1 as in:

 SELECT  
   user,
   ARRAY (SELECT as struct
   step1.page,
   step2.page,
   step3.page
   FROM (SELECT * FROM j.hits WHERE step1 is not null LIMIT 1) step1
   LEFT JOIN (SELECT * FROM j.hits WHERE page = '..'  LIMIT 1) step2 ON user=user
   LEFT JOIN (SELECT * FROM j.hits WHERE page = '..'  LIMIT 1) step3 ON user=user 
   LEFT JOIN (SELECT * FROM j.hits WHERE interaction = '..'  LIMIT 1) size ON user=user  
   GROUP BY ..  
   ) as steps

Then aggregate it in the upper query with COUNTIF conditions

## Looking for a specific condition in an array

Use NOT EXISTS (SELECT * FROM unnest (hits) as x WHERE x.page  = 'condition' ) and EXISTS to satisfy condition of an array.

## Advanced filtering/limiting per conditions

This method applies index to retrieve the position of the pageview/interaction and slice array from there upwards, limiting 5 interactions only.
In subquery, position is limited to 1, not to produce scalar results, whereas in outer query LIMIT 5 ensures next 5 paths from the interaction or pageview that is defined earlier.
ARRAY to string concantenates paths with '--' to build a sequence

ARRAY_TO_STRING (ARRAY (( SELECT  path FROM UNNEST (hits) WITH OFFSET pos WHERE pos >= (SELECT pos FROM unnest (hits) WITH OFFSET pos WHERE REGEXP_CONTAINS(path, 'condition') LIMIT 1) LIMIT 3) ) , '--') as hits_from_step1

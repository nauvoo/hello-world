# Operations in Big Query with arrays

Using arrays for faster and more reliable data processing that can easily scale up (especially for funnel composition)

Google Cloud documentation: https://cloud.google.com/bigquery/docs/reference/standard-sql/arrays#scanning-for-values-that-satisfy-a-condition

Array functions: https://cloud.google.com/bigquery/docs/reference/standard-sql/array_functions

ARRAY_CONCAT_AGG (ARRAY (SELECT as struct field1, field2, field3 FROM UNNEST (hits) ORDER BY sequence) ORDER BY sequence/starttime ASC ) as userHits
* allows to aggregate a bunch of fields into a single object that later can be expanded or deconstructed

### Create a custome index for an array (for instance hits for a customer journey)

WITH OFFSET addition to ARRAY function allows us to create 0 position index for each element in an array. 

    ARRAY (( SELECT AS STRUCT index+1 as sequencenumber,
      field1, field2 FROM UNNEST (userHits) WITH OFFSET AS index 
Where `index+1` will ensure that index starts from 1 but not from 0

### To create funnel with arrays

When array is built (construct array with array func and "select as STRUCT"), one can perform a left self join to outline the steps in the funnel, using LIMIT 1 as in:
```
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
```

Then aggregate it in the upper query with COUNTIF conditions

## Looking for a specific condition in an array

Use NOT EXISTS (SELECT * FROM unnest (hits) as x WHERE x.page  = 'condition' ) and EXISTS to satisfy condition of an array.

## Advanced filtering/limiting per conditions

This method applies index to retrieve the position of the pageview/interaction and slice array from there upwards, limiting 5 interactions only.
In subquery, position is limited to 1, not to produce scalar results, whereas in outer query LIMIT 5 ensures next 5 paths from the interaction or pageview that is defined earlier.
ARRAY to string concantenates paths with '--' to build a sequence

```ARRAY_TO_STRING (ARRAY (( SELECT  path FROM UNNEST (hits) WITH OFFSET pos WHERE pos >= (SELECT pos FROM unnest (hits) WITH OFFSET pos WHERE REGEXP_CONTAINS(path, 'condition') LIMIT 1) LIMIT 3) ) , '--') as hits_from_step1```

## Fast processing with arrays
When building arrays it seems that it processes less resources and generate input faster. Consider this snippet:
```
CREATE TEMPORARY FUNCTION table_range(suffix string) as (suffix BETWEEN '20181008' AND '20181126'); 
CREATE TEMPORARY FUNCTION money(amount INT64) AS (amount / POW(10, 6));
CREATE TEMPORARY FUNCTION sid(fullvisitorId STRING, visitStartTime INT64) AS (CONCAT(fullVisitorId,"|",CAST(visitStartTime AS STRING)));
CREATE TEMPORARY FUNCTION cd(index_var INT64, customDimensions ARRAY<STRUCT<index INT64, value STRING>>) as (
  (SELECT value from unnest(customDimensions) where index = index_var LIMIT 1)
  ); 
  
WITH explore as (
  SELECT
    cd(<dimensionindex>, customDimensions) as identifier, --that serves as an 'umbrella' for each user interaction
    sid(fullvisitorid, visitstarttime) as sid,
    date,
    TIMESTAMP_SECONDS (visitstarttime) as visit_time,
    ARRAY (                                      */ here we build our ARRAY object that contains necessary data */
    SELECT AS STRUCT 
    sid(fullvisitorid, visitstarttime) as sid,
    time as time,
    appinfo.screenname as screen, 
    eventInfo.eventCategory ec,
    eventinfo.eventAction ea, 
    eventinfo.eventLabel el,
    type,
    eCommerceAction.action_type as action_type,
    productSKU as product,
    productQuantity as productqty,
    transaction.transactionId as trans,
    MONEY (transaction.transactionRevenue) rev
  FROM UNNEST (hits) 
  LEFT JOIN UNNEST (product) 
            ) as userhits                       */ end of ARRAY object unnested on hit-level */
  FROM `projectid.datasetid.table_name*`        */ the initial table is not UNNESTED (!), array itself is*/
  WHERE table_range(_TABLE_SUFFIX) 
  AND (SELECT LOGICAL_OR(<condition> is not null) FROM UNNEST (hits) )
```
---
```
SELECT 
identifier,
date as date_session,
visit_time,
 */ Perform count of specific conditions that match the criteria in the ARRAY*/
 
ARRAY (SELECT COUNT (DISTINCT sid) FROM UNNEST (userhits) ) as sessions,
ARRAY (SELECT SUM (IF (type= 'APPVIEW' and screen=<screenname>, 1, 0)) FROM UNNEST (userhits)) as screen_views,
ARRAY_LENGTH (ARRAY (SELECT product FROM UNNEST (userhits) WHERE action_type='2' and product is not null)) as views,
ARRAY (SELECT COUNT(DISTINCT category) FROM unnest (userhits) WHERE product is not null ) as unique_pdpcat_viewed,
 */ ARRAY LENGHT allows to count per specific conditions, like COUNTIF */
FROM explore
```

#### Last part of the query allows to get all the data and unnest it, so that you don't get repeated data in the results table
```
SELECT
identifier as user,
((SELECT * FROM UNNEST (p.screen_views) )) as screen_views,
views,
FROM prelim as p 
*/Where we need to UNNEST those conditions with ARRAY function to avoid repeated data types*/
```


## Frequency of events calculation (credit to post on StackOverflow)
```
CREATE TEMP FUNCTION GetNamesAndCounts(elements ARRAY<STRING>) AS (
  ARRAY(
    SELECT AS STRUCT elem AS interaction, COUNT(*) AS frequency
    FROM UNNEST(elements) AS elem 
    GROUP BY elem
  )
 ```
 
 Actual usage of a function
 
 GetNamesAndCounts (ARRAY (SELECT path FROM UNNEST (userjourney) ORDER BY hitnumber asc) )  events_frequency
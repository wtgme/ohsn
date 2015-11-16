1. get stream from twitter.com (by sample or track with keywords) and store them in stream collections.

2. get users from stream and store them in poi_collections

3. get timelines of users in poi_collection and store them in timeline collections

4. set flag of users in poi collection according to the records in timeline collections.
    "datetime_last_timeline_scrape": last_date, 'timeline_auth_error_flag': False, "timeline_scraped_flag": True, 'timeline_count': count_scraped

5. perform text process with LIWC on users' timeline and store the results in poi collection

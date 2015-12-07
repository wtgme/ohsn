1. get stream from twitter.com (by sample or track with keywords) and store them in stream collections.
    using: stream/streaming_keyword.py and stream/streaming_sample.py

2. get users from stream and store them in poi_collections
    using: stream/streaming_profile.py

3. get seed user from user
    using: stream/seeding_poi.py

4. get user's followee and followees' followees
    using: stream/user_followee.py

4. get timelines of users in poi_collection and store them in timeline collections
    using: stream/streaming_user_timeline.py

5. set flag of users in poi collection according to the records in timeline collections.
    "datetime_last_timeline_scrape": last_date, 'timeline_auth_error_flag': False, "timeline_scraped_flag": True, 'timeline_count': count_scraped
    using: stream/setfalg4poi_timeline.py

5. perform text process with LIWC on users' timeline and store the results in poi collection
    using: analyser/lexiconsmaster/liwc_timeline_processor.py

6. profile text mining to generate gender and weight etc.
    using analyser/textprocessor/description_miner.py

6. network analysis based on users' timelines
    using: analyser/networkminer/timeline_network_miner.py

#!/usr/bin/env python3
'''Task 11 module
'''


def schools_by_topic(mongo_collection, topic):
    '''Return list of school having specific topic
    '''
    topic_filter = {
        'topics': {
            '$elemMatch': {
                '$eq': topic,
            },
        },
    }
    return [doc for doc in mongo_collection.find(topic_filter)]

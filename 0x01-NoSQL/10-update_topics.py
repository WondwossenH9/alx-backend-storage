#!/usr/bin/env python3
'''Task 10 module
'''


def update_topics(mongo_collection, name, topics):
    '''Change all topics of a collection's document based on name
    '''
    mongo_collection.update_many(
        {'name': name},
        {'$set': {'topics': topics}}
    )

import os
import pandas as pd
from pymongo import MongoClient
from scripts.export_data import clean_df

MONGO_URL = os.environ.get('MONGO_URL')

if __name__ == '__main__':
    client = MongoClient(MONGO_URL)
    try:
        collection_raw = client.db.raw
        df = pd.DataFrame(list(collection_raw.find()))
        output_df = clean_df(df)
        print("Finish processing data")
        print(output_df.head(10))
        print(output_df.shape)
        collection_news = client.db.news
        data_dict = output_df.to_dict("records")
        # Insert collection
        collection_news.insert_many(data_dict)
    except Exception as ex:
        print("cannot process data")

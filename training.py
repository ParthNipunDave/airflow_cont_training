import pandas as pd
from sklearn.metrics import r2_score
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from google.cloud import bigquery
from datetime import datetime
from google.cloud import storage
import os


def main():
    client = bigquery.Client()
    table_id = "model_metrics.bike_sharing_metrics"
    storage_client = storage.Client()
    bucket = storage_client.bucket('model-collections')

    columns = ['season', 'yr', 'holiday', 'atemp', 'casual', 'registered']
    data = pd.read_csv('gs://us-central1-my-composer-86198dd4-bucket/dags/day.csv')
    data.drop(['instant', 'dteday'], axis=1, inplace=True)

    train_x, test_x, train_y, test_y = train_test_split(data[columns], data['cnt'], test_size=0.1)
    print('Model Training Started')
    rfc = RandomForestRegressor()
    rfc.fit(train_x, train_y)
    predict = rfc.predict(test_x)
    r2 = r2_score(predict, test_y)
    print('Model Training done....')
    # checking if model is better performer or not

    query = """select max(r2_score) as r2_score from sublime-state-413617.model_metrics.bike_sharing_metrics """
    r2_scores = client.query(query).to_dataframe()['r2_score'].max()
    if r2_scores > r2:
        df = pd.DataFrame(
            [{'Algo': 'RandomForestRegressor', 'R2_Score': r2,
              'Training_Time': datetime.now().strftime('%Y-%b-%d %H:%M:%S')}])
        df.to_gbq(project_id='sublime-state-413617', destination_table=table_id, if_exists='append')
        print('Data Pushed!')

        pickle.dump(rfc, open('bike_sharing_model.sav', 'wb'))
        print('Model Saved!')
        bucket = storage_client.bucket('model-collections')
        blob = bucket.blob('bike_sharing_model.sav')
        blob.upload_from_filename('bike_sharing_model.sav')
        print('Model Pushed!')
    else:
        print("No improvement in model performance!")

    print('Training Completed')

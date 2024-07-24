import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression


class UserPredictor:
    def __init__(self):
        numericf = ['age', 'past_purchase_amt', 'total_seconds', 'num_visits', 'avg_time_per_visit', 'visited_laptop_page']
        numerict = Pipeline(steps = [('imputer', SimpleImputer(strategy ='median')),('scaler', StandardScaler())])
        categoricalf = ['badge', 'last_page_visited']
        # Use OneHotEncoder becuase it returns a more accurate corraltion between non numerical values.
        # https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html
        categoricalt = Pipeline(steps=[('imputer', SimpleImputer(strategy='constant', fill_value ='missing')),('onehot', OneHotEncoder(handle_unknown ='ignore'))])
        preprocessor = ColumnTransformer(transformers=[('num', numerict, numericf),('cat', categoricalt, categoricalf)])
        self.model = Pipeline(steps=[('preprocessor', preprocessor),('classifier', LogisticRegression())])

    def log_features(self, logs):
        features = logs.groupby('user_id').agg({'seconds': ['sum', 'count', 'mean'],'url': [lambda x: x.iloc[-1], lambda x: ('laptop.html' in x.values)]})
        features.columns = ['_'.join(col).strip() for col in features.columns.values]
        features = features.reset_index().rename(columns={'seconds_sum': 'total_seconds', 'seconds_count': 'num_visits', 'seconds_mean': 'avg_time_per_visit', 'url_<lambda_0>': 'last_page_visited', 'url_<lambda_1>': 'visited_laptop_page'})
        if 'visited_laptop_page' not in features.columns:
            features['visited_laptop_page'] = 0
        else:
            features['visited_laptop_page'] = features['visited_laptop_page'].astype(int)  
        return features

    def fit(self, train_users, train_logs, train_y):
        features = self.log_features(train_logs)
        train_X = pd.merge(train_users, features, on = 'user_id', how = 'left')
        train_X = pd.merge(train_X, train_y, on = 'user_id', how = 'inner')
        train_y = train_X['y']
        train_X = train_X.drop(columns=['y'])
        self.model.fit(train_X, train_y.values.ravel())

    def predict(self, test_users, test_logs):
        features = self.log_features(test_logs)
        test_X = pd.merge(test_users, features, on ='user_id', how ='left')
        return self.model.predict(test_X)

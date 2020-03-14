#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

wine_df = pd.read_csv('scripts/winequality-red.csv')
wine_df.columns = [c.replace(' ','_') for c in wine_df.columns]
X = ['alcohol','sulphates','volatile_acidity','total_sulfur_dioxide']

model = GradientBoostingRegressor(n_estimators = 400, max_depth = 5, min_samples_split = 2)
model.fit(wine_df[X], wine_df['quality'])

def predict(dict_values, X=X, model=model):
    x = np.array([float(dict_values[col]) for col in X])
    x = x.reshape(1,-1)
    y_pred = model.predict(x)[0]
    return y_pred
from sklearn.preprocessing import MinMaxScaler
from keras.layers import LSTM, Dense, Dropout
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
import alpaca_trade_api as tradeapi
import datetime
from datetime import date
import numpy as np
import numpy
import tensorflow.keras as keras
import tensorflow as tf
from keras import backend as K

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)


path_api_key = "C:/Users/pchya/Desktop/keys/apikey.txt"
path_api_secret = "C:/Users/pchya/Desktop/keys/apisecret.txt"

f = open(path_api_key, 'r')
API_KEY = f.read()
f = open(path_api_secret, 'r')
API_SECRET = f.read()
f.close()

paper_base_url = 'https://paper-api.alpaca.markets'
live_url = "https://api.alpaca.markets"

api = tradeapi.REST(API_KEY, API_SECRET, live_url, api_version='v2')


delta = datetime.timedelta(days=720)
one_day = datetime.timedelta(days=1)
start_date = date.today() - delta
end_date = date.today() - one_day


def predict_swing_gain(symbol):
    K.clear_session()
    numpy.random.seed(1234)

    df = api.get_bars(symbol, TimeFrame(30, TimeFrameUnit.Minute), start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),
                      adjustment='raw').df
    print(df)

    df = df['open'].values

    segment_length = 500

    df_predict_original = np.array(df[-segment_length:])
    print(df)
    df = df.reshape(-1, 1)
    dataset_train = np.array(df[:])

    if len(df) > 10000:
        dataset_train = np.array(df[-10000:])
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset_train = scaler.fit_transform(dataset_train)

    def create_dataset(df):
        x = []
        y = []
        for i in range(segment_length, df.shape[0]):
            x.append(df[i - segment_length:i, 0])
            y.append(df[i, 0])
        x = np.array(x)
        y = np.array(y)
        return x, y

    x_train, y_train = create_dataset(dataset_train)

    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    model = keras.models.Sequential()
    model.add(LSTM(units=10, return_sequences=True, input_shape=(x_train.shape[1], 1)))
    model.add(LSTM(units=25))
    model.add(Dense(units=1))

    model.compile(loss="mse", optimizer='adam')
    model.fit(x_train, y_train, epochs=100, batch_size=1000, verbose=1, shuffle=True)

    df_predict = df_predict_original
    df = df_predict.reshape(-1, 1)
    dataset_predict = np.array(df)

    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset_predict = scaler.fit_transform(dataset_predict)

    x_predict = []
    x_predict.append(dataset_predict[:, 0])
    x_predict = np.array(x_predict)
    x_predict = np.reshape(x_predict, (x_predict.shape[0], x_predict.shape[1], 1))
    predictions = model.predict(x_predict)
    predictions = scaler.inverse_transform(predictions)
    predict = predictions[0][0]
    print(predict)
    initial_prediction = predict
    df_predict = np.append(df_predict_original, [predict])

    ending_prediction = predict_next(df_predict, model, 100, 1, segment_length)

    del model

    return initial_prediction, ending_prediction

def predict_next(price_data, model, iterations, ending_price, segment_length):
    if iterations > 0:
        df_predict = price_data
        df = df_predict.reshape(-1, 1)
        dataset_predict = np.array(df[-segment_length:])

        scaler = MinMaxScaler(feature_range=(0, 1))
        dataset_predict = scaler.fit_transform(dataset_predict)

        x_predict = []
        x_predict.append(dataset_predict[:, 0])
        x_predict = np.array(x_predict)
        x_predict = np.reshape(x_predict, (x_predict.shape[0], x_predict.shape[1], 1))
        predictions = model.predict(x_predict)
        predictions = scaler.inverse_transform(predictions)
        predict = predictions[0][0]
        print(predict)
        df_predict = np.append(df_predict, [predict])
        iterations -= 1
        ending_price = predict_next(df_predict, model, iterations, predict, segment_length)
        return ending_price
    else:
        return ending_price

print(predict_swing_gain('TSLA'))
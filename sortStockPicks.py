import pandas as pd

predictions_path_name = 'predictions/predictions_2022-04-16.csv'
df = pd.read_csv(predictions_path_name)
df.sort_values(by=['Change'], inplace=True, ascending=False)
        # Set number of stock picks here
for i in range(len(df)):
    print(str(df['Symbol'].iloc[i]) + "," + str(df['Change'].iloc[i]))



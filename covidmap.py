import pandas as pd


def get_zipcode(lat, lon, all_l):
    row = all_l[(all_l['latitude'] == lat) & (all_l['longitude'] == lon)]
    print(row)
    print("*")


if __name__ == "__main__":
    root_path = "/Users/shravya/Documents/CMU/Interactive_Data_Science/Assignments/3/Code2/data/"
    reviews = {'NYC': pd.read_csv(root_path + 'NYC_reviews.csv')}
    NYC_listings = {'01': pd.read_csv(root_path + '2020/NYC/listings_01.csv'),
                    '02': pd.read_csv(root_path + '2020/NYC/listings_02.csv'),
                    '03': pd.read_csv(root_path + '2020/NYC/listings_03.csv'),
                    '04': pd.read_csv(root_path + '2020/NYC/listings_04.csv'),
                    '05': pd.read_csv(root_path + '2020/NYC/listings_05.csv'),
                    '06': pd.read_csv(root_path + '2020/NYC/listings_06.csv'),
                    '07': pd.read_csv(root_path + '2020/NYC/listings_07.csv')}

    covid_data = pd.read_csv(root_path + 'data-by-modzcta.csv')
    covid_data = covid_data.rename(columns={"MODIFIED_ZCTA": "zipcode"})

    for key in NYC_listings.keys():
        df = NYC_listings[key]
        df = df[['zipcode', 'latitude', 'longitude']]
        NYC_listings[key] = df

    all_listings = pd.concat([NYC_listings['01'], NYC_listings['02'], NYC_listings['03'],
                              NYC_listings['04'], NYC_listings['05'], NYC_listings['06'],
                              NYC_listings['07']], ignore_index=True)
    all_listings.drop_duplicates(subset=['zipcode'], inplace=True, keep='last')
    all_listings['latitude'] = pd.to_numeric(all_listings['latitude'])
    all_listings['longitude'] = pd.to_numeric(all_listings['longitude'])

    # Now join zipcode info with covid

    covid_data['zipcode'] = covid_data['zipcode'].apply(str)
    covid_zipcode = covid_data.merge(all_listings, on='zipcode', how='left')

    covid_zipcode = covid_zipcode.dropna(subset=['latitude', 'longitude'])

    # Write to a file
    # covid_zipcode.to_csv('covid_data_cleaned.csv', index=False)

    # Get zipcode for months 8 and 9
    month8 = pd.read_csv(root_path + '2020/NYC/listings_08.csv')
    month9 = pd.read_csv(root_path + '2020/NYC/listings_09.csv')
    NYC_listings = {'01': pd.read_csv(root_path + '2020/NYC/listings_01.csv'),
                    '02': pd.read_csv(root_path + '2020/NYC/listings_02.csv'),
                    '03': pd.read_csv(root_path + '2020/NYC/listings_03.csv'),
                    '04': pd.read_csv(root_path + '2020/NYC/listings_04.csv'),
                    '05': pd.read_csv(root_path + '2020/NYC/listings_05.csv'),
                    '06': pd.read_csv(root_path + '2020/NYC/listings_06.csv'),
                    '07': pd.read_csv(root_path + '2020/NYC/listings_07.csv')}

    for key in NYC_listings.keys():
        df = NYC_listings[key]
        df = df[['id', 'zipcode']]
        NYC_listings[key] = df

    all_listings = pd.concat([NYC_listings['01'], NYC_listings['02'], NYC_listings['03'],
                              NYC_listings['04'], NYC_listings['05'], NYC_listings['06'],
                              NYC_listings['07']], ignore_index=True)
    all_listings.drop_duplicates(subset=['zipcode'], inplace=True, keep='last')

    new_month8 = month8.merge(all_listings, on='id', how='left')
    new_month9 = month9.merge(all_listings, on='id', how='left')

    # Write to a file
    new_month8.to_csv('listing_08_cleaned.csv', index=False)
    new_month9.to_csv('listing_09_cleaned.csv', index=False)



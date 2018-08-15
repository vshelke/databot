import pandas as pd
import json, difflib, math
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from statistics import mean, median, stdev

# load metadata
df = pd.read_csv('dataset.csv')
states_list = df['State'].unique()
districts_list = df['District'].unique()
cols = list(df)
col_stop_words = ['dlhs', 'dise', 'houselisting', 'housing', 'census', 'data', 'tables',
                  'india','india__1','india__2','india__3','india__4','india__5']
stop_words = text.ENGLISH_STOP_WORDS.union(col_stop_words)
char_map = { 
    'percentage': '%'
}
for col in cols:
    if not col in ['State', 'District', 'Tier']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

def filter_meta(arr, query):
    '''Returns the list of matches in given list(arr) by searching in query'''
    return [i for i in arr if isinstance(i, str) and i.lower() in query]

def filter_row(query):
    '''Returns the list of states, district and tiers found in query'''
    return filter_meta(states_list, query), filter_meta(districts_list, query)

def filter_col(query):
    '''Returns the nearest column name and corrected query for the given raw query'''
    col_vectorizer = TfidfVectorizer(stop_words=stop_words)
    cols_with_query = cols.copy()
    col_matrix = col_vectorizer.fit_transform(cols_with_query)
    corrected_query = check_query(query, col_vectorizer.get_feature_names())
    cols_with_query.insert(0, query)
    col_matrix = col_vectorizer.fit_transform(cols_with_query)
    sim_matrix = cosine_similarity(col_matrix[0:1], col_matrix)[0][1:]
    return cols[sim_matrix.argmax(axis=0)], corrected_query

def check_query(query, feature_names, thresh=0.87):
    '''
    Returns the corrected query by checking the features with raw query.
    The `thresh` parameter controls the quality of results
    '''
    state_tokens = [token for token in ' '.join(states_list).lower().split(' ')]
    district_tokens = []
    for token in districts_list:
        if isinstance(token, str):
            district_tokens.extend(token.lower().split(' '))
    feature_names.extend(state_tokens + district_tokens)
    feature_names = set(feature_names)
    tokens = [token for token in query.split(' ')]
    corrected_tokens = tokens
    for i, token in enumerate(tokens):
        for feature in feature_names:
            ratio = difflib.SequenceMatcher(None, token, feature).ratio()
            if ratio > thresh:
                corrected_tokens[i] = feature
    return ' '.join(corrected_tokens)

def preprocess_query(query):
    '''Returns a preprocessed query'''
    query = query.lower()
    for ch in char_map.keys():
        query.replace(ch, char_map[ch])
    return query

def fetch_metric(col_name):
    '''Returns the metric column uses to represent the values'''
    if '(%)' in col_name:
        return '%'
    elif '(Number)' in col_name or '(#)' in col_name:
        return '#'
    else:
        return ''

def fetch_data(state, district, col_name, corrected_query):
    '''Returns the data in dict format by selecting nearest dataframe with provided parameters'''
    data = {
        'meta': {},
        'corrected_query': corrected_query,
        'feature': col_name,
        'metric': fetch_metric(col_name),
        'rows': []
    }
    rows_selected = pd.DataFrame()
    overall_stats = [[],[],[]]
    if len(state) > 0 and len(district) > 0:
        for s in state:
            rows_selected = rows_selected.append(df.loc[df['State'] == s])
        unq_d = row_selected.District.unique()
        for d in district:
            if not d in unq_d:
                rows_selected = rows_selected.append(df.loc[df['District'] == d])
    elif len(state) > 0:
        for s in state:
            rows_selected = rows_selected.append(df.loc[df['State'] == s])
    elif len(district) > 0:
        for d in district:
            rows_selected = rows_selected.append(df.loc[df['District'] == d])
    else:
        # handle if not data found currently uses spell checker
        pass
    if not rows_selected.empty and col_name != 'Unnamed: 0':
        visited_districts = []
        for index, row in rows_selected.iterrows():
            if row['District'] in visited_districts:
                continue
            t_total = rows_selected.loc[(rows_selected['District'] == row['District']) & 
                                        (rows_selected['Tier'] == 'Total')]
            t_rural = rows_selected.loc[(rows_selected['District'] == row['District']) & 
                                        (rows_selected['Tier'] == 'Rural')]
            t_urban = rows_selected.loc[(rows_selected['District'] == row['District']) & 
                                        (rows_selected['Tier'] == 'Urban')]
            total = round(t_total[col_name].values[0], 1) if len(t_total[col_name].values) > 0 else ''
            rural = round(t_rural[col_name].values[0], 1) if len(t_rural[col_name].values) > 0 else ''
            urban = round(t_urban[col_name].values[0], 1) if len(t_urban[col_name].values) > 0 else ''
            resp = {
                'state': row['State'],
                'district': row['District'],
                'tier': {
                    'total': total,
                    'rural': rural,
                    'urban': urban
                }
            }
            if isinstance(total, float) and not math.isnan(total):
                overall_stats[0].append(total)
            if isinstance(rural, float) and not math.isnan(rural):
                overall_stats[1].append(rural)
            if isinstance(urban, float) and not math.isnan(urban):
                overall_stats[2].append(urban)
            data['rows'].append(resp)
            visited_districts.append(row['District'])
    data['meta'] = process_meta(overall_stats)
    return data

def process_meta(overall_stats):
    '''Returns the meta section of the data object'''
    total_mean, total_median, total_stdev = process_stats(overall_stats[0])
    rural_mean, rural_median, rural_stdev = process_stats(overall_stats[1])
    urban_mean, urban_median, urban_stdev = process_stats(overall_stats[2])
    return {
        'total': {
            'mean': total_mean,
            'median': total_median,
            'stdev': total_stdev
        },
        'rural': {
            'mean': rural_mean,
            'median': rural_median,
            'stdev': rural_stdev
        },
        'urban': {
            'mean': urban_mean,
            'median': urban_median,
            'stdev': urban_stdev
        }
    }

def process_stats(arr, precision=2, empty=''):
    '''Returns the statistics for the given array'''
    arr_mean = round(mean(arr), precision) if len(arr) > 0 else empty
    arr_median = round(median(arr), precision) if len(arr) > 0 else empty
    arr_stdev = round(stdev(arr), precision) if len(arr) > 1 else empty
    return arr_mean, arr_median, arr_stdev

def process_query(query):
    '''Returns the data after completely processing the query'''
    query = preprocess_query(query)
    state, district = filter_row(query)
    col_name, corrected_query = filter_col(query)
    return fetch_data(state, district, col_name, corrected_query)

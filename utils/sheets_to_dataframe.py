import pandas as pd

def sheets_to_df(sheets, mode="Columns", df_type="", df_type_columns='*', transpose=False):

    if mode == "rows":
        sheets[0][0] = None

    if transpose:
        df = pd.DataFrame(sheets).T
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
    else:
        df = pd.DataFrame(sheets[1:], columns=sheets[0])

    if mode == "rows":
        df = df.set_index(df.columns[0])

    if df_type_columns == '*':
        df_type_columns = df.columns
    else:
        df_type_columns = [col.strip() for col in df_type_columns.split(',')]

    match df_type:
        case "numeric":
            for column in df_type_columns:
                df[column] = df[column].replace({',': '.'}, regex=True).apply(pd.to_numeric, errors='coerce')
        case "date":
            for column in df_type_columns:
                df[column] = pd.to_datetime(df[column], format='%Y年%m月%d日')

    return df
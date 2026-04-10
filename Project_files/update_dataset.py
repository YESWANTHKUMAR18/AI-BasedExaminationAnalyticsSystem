import pandas as pd

df = pd.read_csv('student_scores_dataset.csv')
rename_map = {
    'history_score': 'tamil_score',
    'math_score': 'maths_score',
    'geography_score': 'computer_science_score'
}
df.rename(columns=rename_map, inplace=True)
df.to_csv('student_scores_dataset.csv', index=False)
print("Dataset columns updated!")

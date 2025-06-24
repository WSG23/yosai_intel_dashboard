import argparse
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib


def main(input_csv: str, model_path: str, vectorizer_path: str) -> None:
    df = pd.read_csv(input_csv)
    if 'header' not in df.columns or 'label' not in df.columns:
        raise ValueError("CSV must contain 'header' and 'label' columns")
    headers = df['header'].astype(str)
    labels = df['label'].astype(str)

    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 4))
    X = vectorizer.fit_transform(headers)

    clf = LogisticRegression(max_iter=1000)
    clf.fit(X, labels)

    joblib.dump(clf, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    print(f"Model saved to {model_path}")
    print(f"Vectorizer saved to {vectorizer_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train column mapping model")
    parser.add_argument("input_csv", help="CSV with 'header' and 'label' columns")
    parser.add_argument("--model-path", default="data/column_model.joblib")
    parser.add_argument("--vectorizer-path", default="data/column_vectorizer.joblib")

    args = parser.parse_args()
    main(args.input_csv, args.model_path, args.vectorizer_path)

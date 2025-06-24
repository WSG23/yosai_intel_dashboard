# Machine-Learned Column Mapping

The column mapper can leverage a supervised model to recognize common header variations.
The provided training script expects a CSV file with `header` and `label` columns.
Run the following to train a new model:

```bash
python scripts/train_column_classifier.py training_data.csv
```

This creates `data/column_model.joblib` and `data/column_vectorizer.joblib` used by
`ColumnMappingService` when `learning_enabled` is enabled in the configuration.

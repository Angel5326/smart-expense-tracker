"""
ML-based category prediction using scikit-learn's Multinomial Naive Bayes.

Usage:
    from .ml_predictor import ml_predict, train_model, MODEL_PATH

Model file: expenses/ml_model.pkl
Training data: user's existing expenses (title + category)
"""
import os
import pickle
from pathlib import Path

from django.conf import settings

MODEL_DIR = Path(settings.BASE_DIR) / 'expenses' / 'ml'
MODEL_DIR.mkdir(exist_ok=True)
MODEL_PATH = MODEL_DIR / 'category_model.pkl'
MIN_SAMPLES = 20  # Training panna minimum records


def train_model(queryset=None):
    """
    Train Naive Bayes model on expense data.
    Returns: dict with status + accuracy
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.pipeline import Pipeline
    except ImportError:
        return {'ok': False, 'message': 'scikit-learn not installed. Run: pip install scikit-learn'}

    if queryset is None:
        from .models import Expense
        queryset = Expense.objects.all()

    data = list(queryset.exclude(category='').values('title', 'category'))
    if len(data) < MIN_SAMPLES:
        return {
            'ok': False,
            'message': f'Need at least {MIN_SAMPLES} labeled expenses to train (have {len(data)}).',
            'count': len(data),
        }

    # Category balance check
    from collections import Counter
    cat_counts = Counter(d['category'] for d in data)
    valid_cats = [c for c, cnt in cat_counts.items() if cnt >= 3]
    data = [d for d in data if d['category'] in valid_cats]

    if len(data) < MIN_SAMPLES:
        return {
            'ok': False,
            'message': f'Not enough data per category. Add more labeled expenses.',
            'count': len(data),
        }

    X = [d['title'] for d in data]
    y = [d['category'] for d in data]

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),
            lowercase=True,
            min_df=1,
            max_features=2000,
            sublinear_tf=True,
        )),
        ('clf', MultinomialNB(alpha=0.5)),
    ])
    pipeline.fit(X, y)

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(pipeline, f)

    return {
        'ok': True,
        'count': len(data),
        'categories': len(set(y)),
        'message': f'Model trained on {len(data)} samples across {len(set(y))} categories.',
    }


def load_model():
    """Load trained model — returns None if not available."""
    if not MODEL_PATH.exists():
        return None
    try:
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return None


def ml_predict(text):
    """
    Predict category using ML model.
    Returns: (category, confidence_percent) or (None, 0) if unavailable.
    """
    model = load_model()
    if model is None or not text:
        return None, 0

    try:
        proba = model.predict_proba([text])[0]
        classes = model.classes_
        best_idx = proba.argmax()
        return str(classes[best_idx]), round(float(proba[best_idx]) * 100)
    except Exception:
        return None, 0


def smart_predict(text):
    """
    Hybrid: Try ML first, fall back to keyword-based prediction.
    Returns: (category, confidence, method)
    """
    from .utils import predict_category

    ml_cat, ml_conf = ml_predict(text)
    if ml_cat and ml_conf >= 40:  # Confidence threshold
        return ml_cat, ml_conf, 'ml'

    kw_cat, kw_conf = predict_category(text)
    return kw_cat, kw_conf, 'keyword'


def model_info():
    """Info about current model."""
    if not MODEL_PATH.exists():
        return {'exists': False, 'size': 0, 'modified': None}

    stat = MODEL_PATH.stat()
    from datetime import datetime
    return {
        'exists': True,
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime),
    }
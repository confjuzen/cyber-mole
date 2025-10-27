"""
Machine Learning-based Data Cleaner
Uses fuzzy matching, clustering, and pattern recognition to clean music data
"""
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from fuzzywuzzy import fuzz
from collections import Counter
import re
import json


class MLDataCleaner:
    """ML-powered data cleaning for music records"""
    
    def __init__(self):
        self.format_mappings = {
            'cd': 'CD',
            'vinyl': 'Vinyl',
            'cassette': 'Cassette',
            'digital': 'Digital',
            '8track': '8-Track',
            'reel': 'Reel-to-Reel'
        }
        
    def clean_data(self, data):
        """Main cleaning pipeline"""
        if isinstance(data, str):
            data = json.loads(data)
        
        df = pd.DataFrame(data)
        
        # Step 1: Normalize formats using fuzzy matching
        df['format'] = df['format'].apply(self._normalize_format)
        
        # Step 2: Normalize genres
        df['genre'] = df['genre'].apply(self._normalize_genre)
        
        # Step 3: Normalize artist names using clustering
        df['artist'] = self._normalize_artists(df['artist'])
        
        # Step 4: Normalize titles
        df['title'] = self._normalize_titles(df)
        
        # Step 5: Group similar records by normalized artist and title, add count
        count_df = df.groupby(['artist', 'title']).size().reset_index(name='count')

        # Dynamic aggregation based on existing columns
        agg_dict = {}
        for col in df.columns:
            if col not in ['artist', 'title']:
                if df[col].dtype in ['int64', 'float64']:
                    # For numeric columns, use mean
                    agg_dict[col] = 'mean'
                else:
                    # For non-numeric columns, use first
                    agg_dict[col] = 'first'
        df = df.groupby(['artist', 'title']).agg(agg_dict).reset_index()
        df = df.merge(count_df, on=['artist', 'title'], how='left')

        # Ensure count column exists (it should be added by the merge, but just in case)
        if 'count' not in df.columns:
            df['count'] = 1
        
        # Step 6: Validate and fix data types
        df = self._validate_data_types(df)
        
        return df.to_dict('records')
    
    def _normalize_format(self, format_val):
        """Normalize format field using fuzzy string matching"""
        # Check for None or NaN
        try:
            if format_val is None or (isinstance(format_val, float) and pd.isna(format_val)):
                return 'Unknown'
        except (ValueError, TypeError):
            pass
        
        format_str = str(format_val).lower().strip()
        
        # Check for empty or nan string
        if format_str in ['nan', 'none', '']:
            return 'Unknown'
        
        # Remove special characters and extra spaces
        format_str = re.sub(r'[^a-z0-9\s]', '', format_str)
        format_str = re.sub(r'\s+', '', format_str)
        
        # Fuzzy match against known formats
        best_match = None
        best_score = 0
        
        for key, value in self.format_mappings.items():
            score = fuzz.ratio(format_str, key)
            if score > best_score:
                best_score = score
                best_match = value
        
        # If confidence is high enough, use the match
        if best_score > 70:
            return best_match
        
        # Handle specific typos
        if 'vynil' in format_str or 'viny' in format_str:
            return 'Vinyl'
        elif 'casset' in format_str:
            return 'Cassette'
        elif 'recod' in format_str:
            return 'Vinyl'
        elif '8trac' in format_str or '8track' in format_str:
            return '8-Track'
        elif 'reel' in format_str:
            return 'Reel-to-Reel'
        elif 'cd' in format_str:
            return 'CD'
        
        return best_match if best_match else 'Unknown'
    
    def _normalize_genre(self, genre_val):
        """Normalize genre field - handle arrays and strings"""
        # Check for None or NaN (handle both scalar and array cases)
        try:
            if genre_val is None or (isinstance(genre_val, float) and pd.isna(genre_val)):
                return 'Unknown'
        except (ValueError, TypeError):
            pass  # If it's an array, continue processing
        
        # Handle array/list genres
        if isinstance(genre_val, (list, np.ndarray)):
            # Take the first genre and normalize it
            if len(genre_val) > 0:
                genre_val = genre_val[0]
            else:
                return 'Unknown'
        
        # Convert to string
        genre_str = str(genre_val).strip()
        
        # Check if it's a string representation of NaN
        if genre_str.lower() in ['nan', 'none', '']:
            return 'Unknown'
        
        # Fix common typos
        if genre_str.lower() == 'rok':
            return 'Rock'
        
        # Title case for consistency
        return genre_str.title()
    
    def _normalize_artists(self, artist_series):
        """Normalize artist names using clustering and fuzzy matching"""
        artists = artist_series.tolist()
        
        # Create normalized versions for comparison
        normalized = []
        for artist in artists:
            # Remove special chars, lowercase, keep spaces
            norm = re.sub(r'[^a-z0-9\s]', '', str(artist).lower())
            normalized.append(norm)
        
        # Use TF-IDF vectorization for similarity
        vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
        
        try:
            X = vectorizer.fit_transform(normalized)
            
            # Use DBSCAN clustering to find similar artist names
            clustering = DBSCAN(eps=0.01, min_samples=1, metric='cosine')
            labels = clustering.fit_predict(X.toarray())
            
            # For each cluster, find the most common "canonical" form
            clusters = {}
            for idx, label in enumerate(labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(artists[idx])
            
            # Map each artist to their canonical form
            artist_mapping = {}
            for label, cluster_artists in clusters.items():
                # Choose the canonical form (most common, or best formatted)
                canonical = self._choose_canonical_artist(cluster_artists)
                for artist in cluster_artists:
                    artist_mapping[artist] = canonical
            
            # Apply mapping
            return artist_series.map(lambda x: artist_mapping.get(x, x))
        
        except Exception as e:
            # Fallback: just title case
            return artist_series.apply(lambda x: str(x).title())
    
    def _choose_canonical_artist(self, artists):
        """Choose the best canonical form from a cluster of similar artists"""
        # Prefer forms with proper spacing and capitalization
        scored = []
        for artist in artists:
            score = 0
            # Prefer spaces over hyphens or no spaces
            if ' ' in artist:
                score += 3
            # Prefer proper capitalization (not all lower or all upper)
            if artist[0].isupper() and not artist.isupper():
                score += 2
            # Prefer longer names (more complete)
            score += len(artist) * 0.1
            scored.append((score, artist))
        
        # Return highest scored
        scored.sort(reverse=True)
        return scored[0][1]
    
    def _choose_canonical_title(self, titles):
        """Choose the best canonical form from a cluster of similar titles"""
        # Prefer forms with proper spacing and capitalization
        scored = []
        for title in titles:
            score = 0
            # Prefer spaces over no spaces
            if ' ' in title:
                score += 3
            # Prefer proper capitalization (not all lower or all upper)
            if title[0].isupper() and not title.isupper():
                score += 2
            # Prefer longer names (more complete)
            score += len(title) * 0.1
            scored.append((score, title))
        
        # Return highest scored
        scored.sort(reverse=True)
        return scored[0][1]
    
    def _normalize_titles(self, df):
        """Normalize title field using clustering and fuzzy matching"""
        titles = df['title'].tolist()
        
        # Create normalized versions for comparison
        normalized = []
        for title in titles:
            # Remove special chars, lowercase, keep spaces
            norm = re.sub(r'[^a-z0-9\s]', '', str(title).lower())
            normalized.append(norm)
        
        # Use TF-IDF vectorization for similarity
        vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
        
        try:
            X = vectorizer.fit_transform(normalized)
            
            # Use DBSCAN clustering to find similar titles
            clustering = DBSCAN(eps=0.01, min_samples=1, metric='cosine')
            labels = clustering.fit_predict(X.toarray())
            
            # For each cluster, find the most common "canonical" form
            clusters = {}
            for idx, label in enumerate(labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(titles[idx])
            
            # Map each title to their canonical form
            title_mapping = {}
            for label, cluster_titles in clusters.items():
                # Choose the canonical form (most common, or best formatted)
                canonical = self._choose_canonical_title(cluster_titles)
                for title in cluster_titles:
                    title_mapping[title] = canonical
            
            # Apply mapping
            return df['title'].map(lambda x: title_mapping.get(x, x))
        
        except Exception as e:
            # Fallback: just title case
            return df['title'].apply(lambda x: str(x).title())
    
    
    def _validate_data_types(self, df):
        """Ensure all fields have correct data types"""
        # Ensure numeric fields are numeric - only for columns that exist
        numeric_fields = ['price', 'release_year', 'historical_sales', 'sales', 'count']
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')
        
        # Fill any NaN values - only for columns that exist
        # Start with default fill values
        fill_values = {
            'artist': 'Unknown Artist',
            'title': 'Unknown Title',
            'genre': 'Unknown',
            'format': 'Unknown',
            'price': 0.0,
            'release_year': 2000,
            'historical_sales': 0,
            'sales': 0,
            'count': 1
        }

        # Only fill values for columns that actually exist
        existing_fill_values = {k: v for k, v in fill_values.items() if k in df.columns}
        df = df.fillna(existing_fill_values)
        
        return df
    
    def get_cleaning_report(self, original_data, cleaned_data):
        """Generate a report on what was cleaned"""
        report = {
            'original_count': len(original_data),
            'cleaned_count': len(cleaned_data),
            'duplicates_removed': len(original_data) - len(cleaned_data),
            'formats_normalized': 0,
            'genres_normalized': 0,
            'artists_normalized': 0
        }
        
        # Count normalizations
        if isinstance(original_data, str):
            original_data = json.loads(original_data)
        
        original_formats = set(str(item.get('format', '')).lower() for item in original_data)
        cleaned_formats = set(str(item.get('format', '')).lower() for item in cleaned_data)
        report['formats_normalized'] = len(original_formats) - len(cleaned_formats)
        
        # Additional summary fields for stock tracking
        try:
            total_stock = 0
            for item in cleaned_data:
                # default to 1 if count missing (each unique is at least 1)
                qty = item.get('count', 1)
                # coerce numeric
                try:
                    qty = int(qty)
                except Exception:
                    qty = 1
                total_stock += max(qty, 0)
            report['total_stock_quantity'] = total_stock
        except Exception:
            report['total_stock_quantity'] = len(original_data)
        
        # Alias for clarity in UI (unique items/SKUs)
        report['unique_records'] = report['cleaned_count']
        
        return report

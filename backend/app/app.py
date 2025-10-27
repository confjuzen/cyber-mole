from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import requests
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
import json

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database setup
engine = create_engine('sqlite:///warehouse.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    artist = Column(String)
    format = Column(String)
    genre = Column(String)
    price = Column(Float)
    stock_count = Column(Integer)
    # Add other fields as needed

Base.metadata.create_all(engine)

SMILE_URL = 'http://localhost:9000'

# Try to import ML cleaner
try:
    from ml_cleaner import MLDataCleaner
    ml_cleaner = MLDataCleaner()
    ML_AVAILABLE = True
    print("✓ ML Cleaner loaded successfully")
except Exception as e:
    ml_cleaner = None
    ML_AVAILABLE = False
    print(f"⚠ ML Cleaner not available: {e}")
    print("  Install dependencies: pip install scikit-learn pandas fuzzywuzzy python-Levenshtein")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'ml_available': ML_AVAILABLE,
        'routes': [rule.rule for rule in app.url_map.iter_rules() if rule.rule.startswith('/')]
    })

@app.route('/raw-data', methods=['GET'])
def get_raw_data():
    with open('./training/data_set_1.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/clean-data', methods=['GET'])
def get_clean_data():
    with open('./training/data_set_1.json', 'r') as f:
        data = json.dumps(json.load(f))
    # Call Smile /clean
    response = requests.post(f'{SMILE_URL}/clean', json={'data': data})
    cleaned = response.json()['cleanedData']
    return jsonify({'cleanedData': cleaned})

@app.route('/upload_dataset', methods=['POST'])
def upload_dataset():
    file = request.files['file']
    data = file.read().decode('utf-8')
    # Call Smile /clean
    response = requests.post(f'{SMILE_URL}/clean', json={'data': data})
    cleaned = response.json()['cleanedData']
    # Store in DB
    session = Session()
    for line in cleaned.split('\n')[1:]:
        if line.strip():
            parts = line.split(',')
            item = Item(title=parts[1], artist=parts[2], format=parts[3], genre=parts[4], price=float(parts[5]), stock_count=int(parts[6]))
            session.add(item)
    session.commit()
    return jsonify({'message': 'Data uploaded and cleaned'})

@app.route('/save-cleaned-data-to-db', methods=['POST'])
def save_cleaned_data_to_db():
    """Save cleaned data directly to the database"""
    session = Session()
    try:
        data = request.json.get('data')
        # Clear existing items
        session.query(Item).delete()
        # Add new items
        for item in data:
            db_item = Item(
                title=item.get('title', ''),
                artist=item.get('artist', ''),
                format=item.get('format', ''),
                genre=item.get('genre', ''),
                price=float(item.get('price', 0)),
                stock_count=int(item.get('stock_count', 0))
            )
            session.add(db_item)
        session.commit()
        return jsonify({'success': True, 'message': 'Cleaned data saved to database'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500
    finally:
        session.close()

@app.route('/get-items', methods=['GET'])
def get_items():
    """Get all items from the database for visualization"""
    session = Session()
    items = session.query(Item).all()
    data = [{
        'id': item.id,
        'title': item.title,
        'artist': item.artist,
        'format': item.format,
        'genre': item.genre,
        'price': item.price,
        'stock_count': item.stock_count
    } for item in items]
    session.close()
    return jsonify(data)

@app.route('/simulate', methods=['POST'])
def simulate():
    # Placeholder for simulation logic
    return jsonify({'sim_id': 1, 'status': 'running'})

@app.route('/ml-clean-data', methods=['GET', 'POST'])
def ml_clean_data():
    """ML-based data cleaning endpoint"""
    # Check if ML is available
    if not ML_AVAILABLE:
        return jsonify({
            'error': 'ML Cleaner not available. Install dependencies: pip install scikit-learn pandas fuzzywuzzy python-Levenshtein',
            'success': False
        }), 503
    
    try:
        # Get data from request or file
        if request.method == 'POST':
            data = request.json.get('data')
        else:
            with open('./training/data_set_1.json', 'r') as f:
                data = json.load(f)
        
        # Ensure data is a list
        if not isinstance(data, list):
            return jsonify({
                'error': f'Expected list, got {type(data).__name__}',
                'success': False
            }), 400
        
        # Clean the data using ML
        cleaned_data = ml_cleaner.clean_data(data)
        
        # Generate cleaning report
        report = ml_cleaner.get_cleaning_report(data, cleaned_data)
        
        return jsonify({
            'cleaned_data': cleaned_data,
            'report': report,
            'success': True
        })
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'success': False
        }), 500

@app.route('/save-cleaned-data', methods=['POST'])
def save_cleaned_data():
    """Save cleaned data to a new file"""
    try:
        cleaned_data = request.json.get('data')
        output_path = './training/cleaned_data.json'

        with open(output_path, 'w') as f:
            json.dump(cleaned_data, f, indent=2)

        return jsonify({
            'message': 'Cleaned data saved successfully',
            'path': output_path,
            'success': True
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5004, allow_unsafe_werkzeug=True)
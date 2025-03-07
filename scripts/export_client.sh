#!/bin/bash

set -ex
echo "exporting monitor_api client to /frontend/"

cd backend || { echo "Error: backend directory not found"; exit 1; }

python -c "
import json; from app.main import app; 
f=open('../frontend/openapi.json', 'w');
json.dump(app.openapi(), f, indent=2); f.close();
cd ..
"
if [ -f "frontend/openapi.json" ]; then
    echo "✓ Schema successfully saved to frontend directory"
else
    echo "Error: Schema file not created"
    exit 1
fi

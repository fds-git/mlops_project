python3 download_model.py
tar -xzvf fitted_model_name.tar.gz
uvicorn server:app --host 0.0.0.0 --port 80 --reload 

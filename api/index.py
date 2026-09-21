from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Esta ruta será accesible desde https://tu-sitio.vercel.app/api/index
@app.route('/api/index', methods=['POST'])
def submit():
    data = request.json
    respuesta = data.get('respuesta')
    
    # Obtenemos la variable de entorno que Neon creó en Vercel
    db_url = os.environ.get('DATABASE_URL') 
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        # Asegúrate de crear esta tabla en la consola de Neon
        cur.execute("INSERT INTO encuestas (respuesta) VALUES (%s)", (respuesta,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "éxito"}), 200
    except Exception as e:
        return jsonify({"status": "error", "detalle": str(e)}), 500
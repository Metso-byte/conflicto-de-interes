from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

@app.route('/api/index', methods=['POST'])
def submit():
    record = request.json
    db_url = os.environ.get('DATABASE_URL') 
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        sql = """
        INSERT INTO encuestas (
            candidato_nombre, candidato_rut, candidato_correo, tipo_conflicto, 
            subcategorias, descripcion, partes, empresa_mencionada, 
            auto_decision, factores_dudas, auto_finanzas, auto_beneficio, 
            detalles_beneficio, propuesta_gestion, otro_conflicto
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores = (
            record.get('candidato_nombre'), record.get('candidato_rut'), record.get('candidato_correo'),
            record.get('tipo_conflicto'), record.get('subcategorias'), record.get('descripcion'),
            record.get('partes'), record.get('empresa_mencionada'), record.get('auto_decision'),
            record.get('factores_dudas'), record.get('auto_finanzas'), record.get('auto_beneficio'),
            record.get('detalles_beneficio'), record.get('propuesta_gestion'), record.get('otro_conflicto')
        )
        
        cur.execute(sql, valores)
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"status": "éxito"}), 200
    except Exception as e:
        return jsonify({"status": "error", "detalle": str(e)}), 500
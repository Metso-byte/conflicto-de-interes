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
        
        # CAMBIO 1: Se agregó 'firma' al final de las columnas y un '%s' extra en VALUES (ahora son 16)
        sql = """
        INSERT INTO encuestas (
            candidato_nombre, candidato_rut, candidato_correo, tipo_conflicto, 
            subcategorias, descripcion, partes, empresa_mencionada, 
            auto_decision, factores_dudas, auto_finanzas, auto_beneficio, 
            detalles_beneficio, propuesta_gestion, otro_conflicto, firma
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # CAMBIO 2: Se agregó record.get('firma') al final de la tupla
        valores = (
            record.get('candidato_nombre'), record.get('candidato_rut'), record.get('candidato_correo'),
            record.get('tipo_conflicto'), record.get('subcategorias'), record.get('descripcion'),
            record.get('partes'), record.get('empresa_mencionada'), record.get('auto_decision'),
            record.get('factores_dudas'), record.get('auto_finanzas'), record.get('auto_beneficio'),
            record.get('detalles_beneficio'), record.get('propuesta_gestion'), record.get('otro_conflicto'),
            record.get('firma')
        )
        
        cur.execute(sql, valores)
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"status": "éxito"}), 200
    except Exception as e:
        return jsonify({"status": "error", "detalle": str(e)}), 500
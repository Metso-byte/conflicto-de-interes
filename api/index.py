from flask import Flask, request, jsonify
import psycopg2
import os
import base64
import requests
import uuid

app = Flask(__name__)

@app.route('/api/index', methods=['POST'])
def submit():
    record = request.json
    db_url = os.environ.get('DATABASE_URL') 
    blob_token = os.environ.get('BLOB_READ_WRITE_TOKEN')
    
    try:
        firma_base64 = record.get('firma')
        firma_url = None
        
        # 1. SUBIR LA FIRMA A VERCEL BLOB
        if firma_base64 and blob_token:
            # Separar el encabezado 'data:image/png;base64,' del contenido real
            if ',' in firma_base64:
                firma_base64 = firma_base64.split(',')[1]
                
            # Decodificar el texto a binario (imagen real)
            img_data = base64.b64decode(firma_base64)
            
            # Generar un nombre único para el archivo basado en el RUT del candidato
            rut_limpio = str(record.get('candidato_rut')).replace('.', '').replace('-', '')
            filename = f"firma_{rut_limpio}_{uuid.uuid4().hex[:6]}.png"
            
            # Hacer la petición PUT a la API REST de Vercel Blob
            headers = {
                "Authorization": f"Bearer {blob_token}"
            }
            blob_response = requests.put(
                f"https://blob.vercel-storage.com/{filename}",
                data=img_data,
                headers=headers
            )
            
            # Extraer la URL pública si la subida fue exitosa
            if blob_response.status_code == 200:
                firma_url = blob_response.json().get('url')
            else:
                raise Exception(f"Error subiendo a Blob: {blob_response.text}")

        # 2. GUARDAR LOS DATOS EN NEON POSTGRESQL
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        sql = """
        INSERT INTO respuestas_ddc (
            candidato_nombre, candidato_rut, candidato_correo, tipo_conflicto, 
            subcategorias, descripcion, partes, empresa_mencionada, 
            auto_decision, factores_dudas, auto_finanzas, auto_beneficio, 
            detalles_beneficio, propuesta_gestion, otro_conflicto, firma
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores = (
            record.get('candidato_nombre'), record.get('candidato_rut'), record.get('candidato_correo'),
            record.get('tipo_conflicto'), record.get('subcategorias'), record.get('descripcion'),
            record.get('partes'), record.get('empresa_mencionada'), record.get('auto_decision'),
            record.get('factores_dudas'), record.get('auto_finanzas'), record.get('auto_beneficio'),
            record.get('detalles_beneficio'), record.get('propuesta_gestion'), record.get('otro_conflicto'),
            firma_url # Aquí se guarda la URL web (ej: https://...vercel-storage.com/firma_123.png)
        )
        
        cur.execute(sql, valores)
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"status": "éxito"}), 200
    except Exception as e:
        return jsonify({"status": "error", "detalle": str(e)}), 500
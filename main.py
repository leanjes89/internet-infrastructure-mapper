import os
import requests
import csv
import time
import io
from flask import Flask
from google.cloud import storage

app = Flask(__name__)

# CONFIGURACIÓN
NOMBRE_BUCKET = "TU_BUCKET_AQUI"

@app.route("/", methods=["GET", "POST"])
def investigar():
    print("[*] Inicio de solicitud recibida.")
    ips_sospechosas = # Lista de IPs a investigar
    
    output = io.StringIO()
    escritor = csv.writer(output)
    escritor.writerow(["IP", "ASN", "Organizacion"])

    try:
        for ip in ips_sospechosas:
            # Consulta RIPE
            res = requests.get(f"https://stat.ripe.net/data/network-info/data.json?resource={ip}", timeout=10).json()
            asns = res.get('data', {}).get('asns', ['?'])
            asn = asns[0] if asns else '?'
            
            res_as = requests.get(f"https://stat.ripe.net/data/as-overview/data.json?resource=AS{asn}", timeout=10).json()
            org = res_as.get('data', {}).get('holder', 'Unknown')
            
            escritor.writerow([ip, f"AS{asn}", org])
            time.sleep(0.5)

        # Subida a Storage
        client = storage.Client()
        bucket = client.bucket(NOMBRE_BUCKET)
        timestamp = int(time.time())
        blob = bucket.blob(f"cloud_reports/investigacion_{timestamp}.csv")
        blob.upload_from_string(output.getvalue(), content_type='text/csv')
        
        return f"Éxito: Reporte investigacion_{timestamp}.csv creado.", 200

    except Exception as e:
        print(f"[!] ERROR FATAL: {str(e)}")
        return f"Error interno: {str(e)}", 500

if __name__ == "__main__":
    # Esto es lo que soluciona el error del puerto 8080
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
from flask import Flask, render_template, request, jsonify
from utils.vrp_algorithm import VRPOptimizer, CIUDADES_COORDENADAS
from routes.vrp import vrp_bp

app = Flask(__name__)

# Registrar el blueprint de la API VRP
app.register_blueprint(vrp_bp, url_prefix='/api/vrp')

@app.route('/')
def index():
    # Pasar las ciudades disponibles a la plantilla
    return render_template('index.html', ciudades=CIUDADES_COORDENADAS.keys())

@app.route('/optimizar', methods=['POST'])
def optimizar():
    try:
        # Obtener datos del formulario
        ciudad_almacen = request.form.get('almacen')
        max_carga = int(request.form.get('max_carga'))
        
        # Obtener pedidos para cada ciudad
        pedidos = {}
        for ciudad in CIUDADES_COORDENADAS.keys():
            pedido_value = request.form.get(f'pedido_{ciudad}', '0')
            pedidos[ciudad] = int(pedido_value) if pedido_value.strip() else 0
        
        # Verificar que se haya seleccionado un almacén válido
        if ciudad_almacen not in CIUDADES_COORDENADAS:
            return jsonify({'error': 'Ciudad de almacén no válida'}), 400
            
        # Coordenadas del almacén seleccionado
        almacen_coords = CIUDADES_COORDENADAS[ciudad_almacen]
        
        # Inicializar el optimizador
        optimizer = VRPOptimizer(CIUDADES_COORDENADAS, pedidos, almacen_coords, max_carga)
        
        # Obtener rutas optimizadas
        resultados = optimizer.optimizar_rutas()
        
        # Agregar datos del almacén y coordenadas para el frontend
        response_data = {
            'almacen': ciudad_almacen,
            'almacen_coords': almacen_coords,
            'ciudades_coords': CIUDADES_COORDENADAS,
            'rutas': resultados
        }
        
        return render_template('results.html', data=response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para documentación de la API
@app.route('/api')
def api_docs():
    return render_template('api_docs.html')

if __name__ == '__main__':
    app.run(debug=True)
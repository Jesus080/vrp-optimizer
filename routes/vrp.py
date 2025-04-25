from flask import Blueprint, request, jsonify
from utils.vrp_algorithm import VRPOptimizer, CIUDADES_COORDENADAS

# Crear un Blueprint para las rutas de la API VRP
vrp_bp = Blueprint('vrp', __name__)

@vrp_bp.route('/optimizar', methods=['POST'])
def optimizar_rutas():
    """
    Endpoint para optimizar rutas basado en parámetros recibidos por POST.
    Espera recibir un JSON con:
    - almacen: Ciudad donde se encuentra el almacén
    - max_carga: Capacidad máxima del vehículo
    - pedidos: Diccionario con la cantidad de pedidos por ciudad
    
    Retorna:
    - JSON con las rutas optimizadas, métricas y coordenadas
    """
    try:
        # Obtener datos del request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se recibieron datos. Se espera un JSON con almacen, max_carga y pedidos.'
            }), 400
        
        # Validar que estén todos los campos requeridos
        if 'almacen' not in data:
            return jsonify({
                'success': False,
                'error': 'Falta el campo "almacen" en los datos recibidos.'
            }), 400
            
        if 'max_carga' not in data:
            return jsonify({
                'success': False,
                'error': 'Falta el campo "max_carga" en los datos recibidos.'
            }), 400
        
        ciudad_almacen = data.get('almacen')
        max_carga = int(data.get('max_carga'))
        pedidos = data.get('pedidos', {})
        
        # Validar almacén
        if ciudad_almacen not in CIUDADES_COORDENADAS:
            return jsonify({
                'success': False,
                'error': f'Ciudad de almacén "{ciudad_almacen}" no válida. Opciones disponibles: {list(CIUDADES_COORDENADAS.keys())}'
            }), 400
            
        # Validar capacidad máxima
        if max_carga <= 0:
            return jsonify({
                'success': False,
                'error': 'La capacidad máxima debe ser mayor que cero.'
            }), 400
            
        # Completar pedidos faltantes con 0
        for ciudad in CIUDADES_COORDENADAS.keys():
            if ciudad not in pedidos:
                pedidos[ciudad] = 0
        
        # Validar pedidos
        for ciudad, cantidad in pedidos.items():
            if ciudad not in CIUDADES_COORDENADAS:
                return jsonify({
                    'success': False,
                    'error': f'Ciudad "{ciudad}" no reconocida en los pedidos.'
                }), 400
            
            try:
                pedidos[ciudad] = int(cantidad)
                if pedidos[ciudad] < 0:
                    return jsonify({
                        'success': False,
                        'error': f'La cantidad de pedidos para {ciudad} debe ser mayor o igual a cero.'
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': f'La cantidad de pedidos para {ciudad} debe ser un número entero.'
                }), 400
        
        # Coordenadas del almacén seleccionado
        almacen_coords = CIUDADES_COORDENADAS[ciudad_almacen]
        
        # Inicializar el optimizador
        optimizer = VRPOptimizer(CIUDADES_COORDENADAS, pedidos, almacen_coords, max_carga)
        
        # Obtener rutas optimizadas
        resultados = optimizer.optimizar_rutas()
        
        # Formar respuesta
        response_data = {
            'success': True,
            'almacen': ciudad_almacen,
            'almacen_coords': almacen_coords,
            'max_carga': max_carga,
            'ciudades_coords': CIUDADES_COORDENADAS,
            'rutas': resultados,
            'total_rutas': len(resultados)
        }
        
        # Calcular estadísticas globales
        distancia_total = sum(r['distancia_total'] for r in resultados)
        consumo_total = sum(r['consumo_gasolina'] for r in resultados)
        tiempo_total = sum(r['tiempo_operacion'] for r in resultados)
        
        response_data['resumen'] = {
            'distancia_total': round(distancia_total, 2),
            'consumo_total': round(consumo_total, 2),
            'tiempo_total': round(tiempo_total, 2)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al procesar la solicitud: {str(e)}'
        }), 500

@vrp_bp.route('/ciudades', methods=['GET'])
def obtener_ciudades():
    """
    Endpoint para obtener la lista de ciudades disponibles
    
    Retorna:
    - JSON con la lista de ciudades y sus coordenadas
    """
    try:
        return jsonify({
            'success': True,
            'ciudades': list(CIUDADES_COORDENADAS.keys()),
            'coordenadas': CIUDADES_COORDENADAS
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@vrp_bp.route('/simular', methods=['GET'])
def simular_datos():
    """
    Endpoint para generar datos de ejemplo para pruebas
    
    Retorna:
    - JSON con datos de ejemplo para usar en la API
    """
    import random
    
    # Seleccionar una ciudad aleatoria para el almacén
    ciudad_almacen = random.choice(list(CIUDADES_COORDENADAS.keys()))
    
    # Generar pedidos aleatorios
    pedidos = {}
    for ciudad in CIUDADES_COORDENADAS.keys():
        # Generar un número aleatorio entre 0 y 10
        pedidos[ciudad] = random.randint(0, 10)
    
    # Capacidad máxima aleatoria entre 10 y 30
    max_carga = random.randint(10, 30)
    
    return jsonify({
        'success': True,
        'ejemplo_datos': {
            'almacen': ciudad_almacen,
            'max_carga': max_carga,
            'pedidos': pedidos
        },
        'instrucciones': 'Estos son datos simulados para probar la API. Envíalos en formato JSON al endpoint /api/vrp/optimizar mediante una solicitud POST.'
    })

# Endpoint adicional para verificar el estado de la API
@vrp_bp.route('/status', methods=['GET'])
def status():
    return jsonify({
        'success': True,
        'status': 'API VRP operativa',
        'endpoints': {
            '/api/vrp/optimizar': 'POST - Optimiza rutas basadas en parámetros',
            '/api/vrp/ciudades': 'GET - Lista de ciudades disponibles',
            '/api/vrp/simular': 'GET - Genera datos de ejemplo'
        }
    })
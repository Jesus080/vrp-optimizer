import math
from operator import itemgetter

class VRPOptimizer:
    def __init__(self, coord, pedidos, almacen, max_carga):
        self.coord = coord
        self.pedidos = pedidos
        self.almacen = almacen
        self.max_carga = max_carga
        self.consumo_por_km = 0.10  # Litros de gasolina por kilómetro
        self.velocidad_promedio = 40  # Kilómetros por hora

    def distancia(self, coord1, coord2):
        lat1 = coord1[0]
        lon1 = coord1[1]
        lat2 = coord2[0]
        lon2 = coord2[1]
        # Usando la fórmula de la distancia euclidiana
        return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

    def en_ruta(self, rutas, c):
        for r in rutas:
            if c in r:
                return r
        return None

    def peso_ruta(self, ruta):
        total = 0
        for c in ruta:
            total = total + self.pedidos[c]
        return total

    def calcular_distancia_total(self, ruta):
        distancia_total = 0
        # Distancia desde el almacén al primer cliente
        distancia_total += self.distancia(self.almacen, self.coord[ruta[0]])
        # Distancia entre los clientes de la ruta
        for i in range(len(ruta) - 1):
            distancia_total += self.distancia(self.coord[ruta[i]], self.coord[ruta[i + 1]])
        # Distancia desde el último cliente al almacén
        distancia_total += self.distancia(self.coord[ruta[-1]], self.almacen)
        return distancia_total

    def optimizar_rutas(self):
        # Calcular ahorros
        s = {}
        for c1 in self.coord:
            for c2 in self.coord:
                if c1 != c2:
                    if not (c2, c1) in s:  # Evitar duplicados
                        d_c1_c2 = self.distancia(self.coord[c1], self.coord[c2])
                        d_c1_almacen = self.distancia(self.coord[c1], self.almacen)
                        d_c2_almacen = self.distancia(self.coord[c2], self.almacen)
                        s[(c1, c2)] = d_c1_almacen + d_c2_almacen - d_c1_c2

        # Ordenar ahorros
        s = sorted(s.items(), key=itemgetter(1), reverse=True)

        # Construir rutas
        rutas = []
        for k, v in s:
            rc1 = self.en_ruta(rutas, k[0])
            rc2 = self.en_ruta(rutas, k[1])
            if rc1 is None and rc2 is None:
                if self.peso_ruta([k[0], k[1]]) <= self.max_carga:
                    rutas.append([k[0], k[1]])
            elif rc1 is not None and rc2 is None:
                if rc1[0] == k[0]:
                    if self.peso_ruta(rc1) + self.pedidos[k[1]] <= self.max_carga:
                        rutas[rutas.index(rc1)].insert(0, k[1])
                elif rc1[-1] == k[0]:
                    if self.peso_ruta(rc1) + self.pedidos[k[1]] <= self.max_carga:
                        rutas[rutas.index(rc1)].append(k[1])
            elif rc1 is None and rc2 is not None:
                if rc2[0] == k[1]:
                    if self.peso_ruta(rc2) + self.pedidos[k[0]] <= self.max_carga:
                        rutas[rutas.index(rc2)].insert(0, k[0])
                elif rc2[-1] == k[1]:
                    if self.peso_ruta(rc2) + self.pedidos[k[0]] <= self.max_carga:
                        rutas[rutas.index(rc2)].append(k[0])
            elif rc1 is not None and rc2 is not None and rc1 != rc2:
                if rc1[0] == k[0] and rc2[-1] == k[1]:
                    if self.peso_ruta(rc1) + self.peso_ruta(rc2) <= self.max_carga:
                        rutas[rutas.index(rc2)].extend(rc1)
                        rutas.remove(rc1)
                elif rc1[-1] == k[0] and rc2[0] == k[1]:
                    if self.peso_ruta(rc1) + self.peso_ruta(rc2) <= self.max_carga:
                        rutas[rutas.index(rc1)].extend(rc2)
                        rutas.remove(rc2)

        # Ciudades no asignadas a rutas
        ciudades_en_rutas = set()
        for ruta in rutas:
            for ciudad in ruta:
                ciudades_en_rutas.add(ciudad)
        
        # Agregar ciudades no asignadas como rutas individuales
        for ciudad in self.coord:
            if ciudad not in ciudades_en_rutas and self.pedidos[ciudad] > 0:
                if self.pedidos[ciudad] <= self.max_carga:
                    rutas.append([ciudad])

        # Calcular métricas para cada ruta
        resultados_rutas = []
        for ruta in rutas:
            distancia_total = self.calcular_distancia_total(ruta)
            consumo_gasolina = distancia_total * self.consumo_por_km
            tiempo_operacion = distancia_total / self.velocidad_promedio
            
            resultados_rutas.append({
                'ruta': ruta,
                'distancia_total': round(distancia_total, 2),
                'consumo_gasolina': round(consumo_gasolina, 2),
                'tiempo_operacion': round(tiempo_operacion, 2),
                'carga_total': self.peso_ruta(ruta)
            })
            
        return resultados_rutas

# Coordenadas de las ciudades (latitud, longitud) - Valores reales para México
CIUDADES_COORDENADAS = {
    'EDO.MEX': (19.293754972996233, -99.65349622329659),
    'QRO': (20.588557, -100.389888),
    'CDMX': (19.433506877145376, -99.13292262466808),
    'SLP': (22.15001704351762, -100.97468793960823),
    'MTY': (25.675146250830167, -100.2870064765848),
    'PUE': (19.071048558430704, -98.31978216159897),
    'GDL': (20.67693892128966, -103.34699075525309),
    'MICH': (19.702537822286565, -101.19172866102593),
    'SON': (30.29695097177479, -110.33288343194367)
}
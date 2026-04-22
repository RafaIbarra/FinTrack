from collections import Counter

def resumen_movimientos_gastos_usuario(data):
    movimientos_data = data

    # Cantidad por empresa (por ID)
    cantidad_por_empresa = Counter(m['Empresa'] for m in movimientos_data)

    # Cantidad por gasto (por ID de GastoUsuario)
    cantidad_por_gasto = Counter(
        gasto['GastoUsuario'] 
        for movimiento in movimientos_data 
        for gasto in movimiento.get('DetalleGastos', [])
    )

    # Cantidad por medio de pago (por ID de MedioPago)
    cantidad_por_medio = Counter(
        medio['MedioPago'] 
        for movimiento in movimientos_data 
        for medio in movimiento.get('DetalleMediosPagos', [])
    )
    resultado={
        'CantidadEmpresa':dict(cantidad_por_empresa),
        'CantidadGastos':dict(cantidad_por_gasto),
        'CantidadMedios':dict(cantidad_por_medio),
        
    }
    # Resultados
    print("Cantidad por empresa (ID):", dict(cantidad_por_empresa))
    print("Cantidad por gasto (ID):", )
    print("Cantidad por medio pago (ID):", dict(cantidad_por_medio))
    return resultado
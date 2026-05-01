from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum

from FinTrackApp.Modelos.MovimientosGastos import MovimientosGastos
from FinTrackApp.Modelos.MovimientosIngresos import MovimientosIngresos


from FinTrackApp.Serializadores.SerilizadoresModelos.MovimientosGastosSerializers import InfoMovimientosGastosSerializer
from FinTrackApp.Serializadores.SerilizadoresModelos.MovimientosIngresosSerializers import InfoMovimientoIngresoSerializer

from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken
class ResumenOperacionesMes(APIView):

    @AutenticacionToken
    def get(self, request, anno, mes, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            id_usuario = user_info.get('usuario_id')

            movimientos_gastos = MovimientosGastos.objects.filter(
                Usuario_id=id_usuario,
                FechaGasto__year=anno,
                FechaGasto__month=mes
            ).annotate(
                TotalMovimiento=Sum('movimiento_gasto_cabecera_detalle__MontoGasto')
            ).order_by('Id')

            if movimientos_gastos.exists():
                data_detalle_gastos = InfoMovimientosGastosSerializer(
                    movimientos_gastos, many=True
                ).data
            else:
                data_detalle_gastos = []

            movimientos_ingresos = MovimientosIngresos.objects.filter(
                Usuario_id=id_usuario,
                FechaIngreso__year=anno,
                FechaIngreso__month=mes
            ).order_by('Id')

            if movimientos_ingresos.exists():
                data_detalle_ingresos = InfoMovimientoIngresoSerializer(
                    movimientos_ingresos, many=True
                ).data
            else:
                data_detalle_ingresos = []

            resultado = self._calcular_resumen(
                data_detalle_gastos, data_detalle_ingresos
            )

            return Response(resultado, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'message': f'Error interno del servidor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _calcular_resumen(self, detalle_gastos, detalle_ingresos):

        # ========== RESULTADO DEL MES ==========
        total_egresos = sum(g['TotalMovimiento'] for g in detalle_gastos)
        cantidad_egresos = len(detalle_gastos)
        total_ingresos = sum(i['MontoIngreso'] for i in detalle_ingresos)
        cantidad_ingresos = len(detalle_ingresos)

        resultado_mes = {
            "TotalGasto": total_egresos,
            "cantidadGasto": cantidad_egresos,
            "TotalIngreso": total_ingresos,
            "CantidadIngreso": cantidad_ingresos,
            "Resultado": total_ingresos - total_egresos,
            "PorcentajeUtilizado": round(
                (total_egresos / total_ingresos * 100), 2
            ) if total_ingresos > 0 else 0
        }

        # ========== GASTOS POR CATEGORÍA ==========
        categorias = {}
        for gasto in detalle_gastos:
            for detalle in gasto.get('DetalleGastos', []):
                cat = detalle['NombreCategoriaGasto']
                if cat not in categorias:
                    categorias[cat] = {"total": 0, "cantidad": 0}
                categorias[cat]["total"] += detalle['MontoGasto']
                categorias[cat]["cantidad"] += 1

        resumen_gastos_categoria = [
            {
                "CategoriaGasto": cat,
                "TotalCategoria": v["total"],
                "Cantidad": v["cantidad"],
                "Porcentaje": round(
                    (v["total"] / total_egresos * 100), 2
                ) if total_egresos > 0 else 0
            }
            for cat, v in categorias.items()
        ]

        # ========== GASTOS POR NOMBRE (NUEVO) ==========
        nombres_gasto = {}
        for gasto in detalle_gastos:
            for detalle in gasto.get('DetalleGastos', []):
                nombre = detalle['NombreGasto']
                if nombre not in nombres_gasto:
                    nombres_gasto[nombre] = {"total": 0, "cantidad": 0}
                nombres_gasto[nombre]["total"] += detalle['MontoGasto']
                nombres_gasto[nombre]["cantidad"] += 1

        resumen_gastos_nombre = [
            {
                "ConceptGasto": nombre,
                "TotalConcepto": v["total"],
                "CantidadConcepto": v["cantidad"],
                "Porcentaje": round(
                    (v["total"] / total_egresos * 100), 2
                ) if total_egresos > 0 else 0
            }
            for nombre, v in nombres_gasto.items()
        ]

        # ========== INGRESOS ==========
        tipos = {}
        for ingreso in detalle_ingresos:
            tipo = ingreso['NombreIngreso']
            if tipo not in tipos:
                tipos[tipo] = {"total": 0, "cantidad": 0}
            tipos[tipo]["total"] += ingreso['MontoIngreso']
            tipos[tipo]["cantidad"] += 1

        resumen_ingresos = [
            {
                "NombreIngreso": tipo,
                "TotalIngreso": v["total"],
                "Cantidad": v["cantidad"],
                "Porcentaje": round(
                    (v["total"] / total_ingresos * 100), 2
                ) if total_ingresos > 0 else 0
            }
            for tipo, v in tipos.items()
        ]

        # ========== MEDIOS DE PAGO ==========
        medios = {}
        for gasto in detalle_gastos:
            for medio in gasto.get('DetalleMediosPagos', []):
                nombre = medio['NombreMedioPago']
                if nombre not in medios:
                    medios[nombre] = {"total": 0, "cantidad": 0}
                medios[nombre]["total"] += medio['MontoMedioPago']
                medios[nombre]["cantidad"] += 1

        resumen_medios = [
            {
                "MedioPago": nombre,
                "TotalMedioPago": v["total"],
                "Cantidad": v["cantidad"],
                "Porcentaje": round(
                    (v["total"] / total_egresos * 100), 2
                ) if total_egresos > 0 else 0
            }
            for nombre, v in medios.items()
        ]

        return {
            "ResultadoDelMes": resultado_mes,
            "ResumenPorTipos": {
                "GastosPorCategoria": resumen_gastos_categoria,
                
                "Ingresos": resumen_ingresos
            },
            "ResumenConceptosGastos":resumen_gastos_nombre,
            "ResumenPorMediosDePagos": resumen_medios
        }
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
import calendar

from FinTrackApp.Modelos.MovimientosGastos import MovimientosGastos
from FinTrackApp.Modelos.MovimientosIngresos import MovimientosIngresos


from FinTrackApp.Serializadores.SerilizadoresModelos.MovimientosGastosSerializers import InfoMovimientosGastosSerializer
from FinTrackApp.Serializadores.SerilizadoresModelos.MovimientosIngresosSerializers import InfoMovimientoIngresoSerializer


from .generar_datos import * 
from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken
class EstadisticaMes(APIView):

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
                data_detalle_gastos = InfoMovimientosGastosSerializer(movimientos_gastos, many=True).data
                resultado_gastos = resumen_gastos(data_detalle_gastos)
                
            else:
                resultado_gastos = []
                data_detalle_gastos=[]
                

            movimientos_ingresos = MovimientosIngresos.objects.filter(
                Usuario_id=id_usuario,
                FechaIngreso__year=anno,
                FechaIngreso__month=mes
            ).order_by('Id')



            if movimientos_ingresos.exists():
                data_detalle_ingresos = InfoMovimientoIngresoSerializer(movimientos_ingresos, many=True).data
                resultado_ingresos = resumen_ingresos(data_detalle_ingresos)
                
            else:
                resultado_ingresos = []
                

            ultimo_dia = calendar.monthrange(anno, mes)[1]
            mes_poner=f'0{mes}' if mes <10 else mes
            periodo=f'01/{mes_poner}/{anno} al {ultimo_dia}/{mes_poner}/{anno}'

            data_gastos = resultado_gastos["TotalesGastos"] if resultado_gastos else {}
            data_ingresos = resultado_ingresos["TotalesIngresos"] if resultado_ingresos else {}
            resultado_unido = {**data_gastos, **data_ingresos}

            if resultado_ingresos:
                total_ingreso=resultado_ingresos["TotalesIngresos"]["TotalIngreso"]
            else:
                total_ingreso=0


            if resultado_gastos:
                total_gasto=resultado_gastos["TotalesGastos"]["TotalGasto"]
            else:
                total_gasto=0

            if data_detalle_gastos:
                gastos_semanales=resumen_gastos_por_semana(data_detalle_gastos,anno,mes,total_gasto)
            else:
                gastos_semanales=[]

            resultado=total_ingreso - total_gasto

            porcentaje_resultado=0.0
            if total_ingreso >0 and total_gasto >0:
                porcentaje_resultado=round((total_gasto / total_ingreso * 100), 2)
            
            
            resultado_unido["Resultado"]=resultado
            resultado_unido["PorcentajeUtilizado"]=porcentaje_resultado

            
            data={
                'Periodo': periodo,
                "ResultadoDelMes":resultado_unido,
                "GastosPorCategoria": resultado_gastos["GastosPorCategoria"] if resultado_gastos else [],
                "GastosPorConceptos": resultado_gastos["ResumenConceptosGastos"] if resultado_gastos else [] ,
                "ResumenMediosDePagos": resultado_gastos["ResumenPorMediosDePagos"]if resultado_gastos else [],
                "GastosSemana":gastos_semanales,
                "ConceptoIngresos":resultado_ingresos["ConceptoIngresos"] if resultado_ingresos else [],
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'message': f'Error interno del servidor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
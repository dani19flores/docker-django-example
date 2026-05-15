import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from django.conf import settings
from django.shortcuts import render
from django import get_version

# --- TU CLASE DEL EJERCICIO ANTERIOR ---
import io # No olvides agregar esta importación al principio del archivo

class AnalizadorDemografico:
    def __init__(self):
        self.nombre_proyecto = "Fundamentos de Linux e Introducción a Django"
        # Ruta según tu estructura de carpetas
        self.public_dir = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'public'))
        self.csv_path = os.path.join(self.public_dir, 'SYB66_246_202310_Population Growth, Fertility and Mortality Indicators.csv')
        self.ruta_grafico = os.path.join(self.public_dir, 'images', 'grafico.png')

    def generar_grafico(self):
        try:
            print(f"DEBUG: Procesando archivo en: {self.csv_path}")

            # --- PASO 1: LIMPIEZA DE COMILLAS EXTERNAS ---
            # Leemos el archivo y quitamos las comillas que envuelven cada línea
            with open(self.csv_path, 'r', encoding='latin1') as f:
                lineas = f.readlines()
            
            lineas_limpias = []
            for line in lineas:
                line = line.strip()
                if line.startswith('"') and line.endswith('"'):
                    line = line[1:-1] # Quitamos la primera y última comilla
                line = line.replace('""', '"') # Corregimos comillas dobles internas
                lineas_limpias.append(line + '\n')
            
            # Convertimos las líneas limpias en un flujo que Pandas pueda leer
            contenido_limpio = io.StringIO("".join(lineas_limpias))

            # --- PASO 2: CARGA CON PANDAS ---
            # Ahora que las líneas no tienen comillas externas, las 7 columnas aparecerán
            df = pd.read_csv(contenido_limpio, skiprows=1, header=None)
            
            # Asignamos nombres (el archivo tiene 7 columnas reales)
            df.columns = ['Region', 'Name', 'Year', 'Series', 'Value', 'Footnotes', 'Source']

            # --- PASO 3: PROCESAMIENTO ---
            # Filtrar por año 2020
            df_2020 = df[df['Year'].astype(str).str.contains('2020')].copy()
            
            # Limpiar valores numéricos (quitar comas de miles)
            df_2020['Value'] = pd.to_numeric(df_2020['Value'].astype(str).str.replace(',', '', regex=True), errors='coerce')
            
            # Crear tabla pivote
            df_pivot = df_2020.pivot_table(index='Name', columns='Series', values='Value')
            
            # Limpiar nombres de columnas del pivote
            df_pivot.columns = [col.split(':')[0].strip() for col in df_pivot.columns]

            # Buscar las columnas necesarias usando palabras clave
            col_mortalidad = [c for c in df_pivot.columns if 'Infant mortality' in c][0]
            col_esperanza = [c for c in df_pivot.columns if 'Life expectancy' in c][0]

            # --- PASO 4: GRÁFICO ---
            plt.figure(figsize=(10, 6))
            sns.set_style("whitegrid")
            sns.regplot(data=df_pivot, x=col_mortalidad, y=col_esperanza, 
                        scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
            
            plt.title('Relación: Mortalidad Infantil vs Esperanza de Vida (2020)')
            plt.xlabel('Mortalidad Infantil (por 1,000 nacimientos)')
            plt.ylabel('Esperanza de Vida (años)')
            
            # Guardar
            os.makedirs(os.path.dirname(self.ruta_grafico), exist_ok=True)
            plt.savefig(self.ruta_grafico)
            plt.close()
            
            print(f"DEBUG: ¡Éxito total! Gráfico creado en {self.ruta_grafico}")
            return True

        except Exception as e:
            print(f"DEBUG ERROR DETALLADO: {e}")
            return False

# --- LA VISTA QUE CONECTA TODO ---
def home(request):
    # Instanciamos la clase
    analizador = AnalizadorDemografico()
    
    # Ejecutamos el método que genera el gráfico
    grafico_exitoso = analizador.generar_grafico()
    
    context = {
        "debug": settings.DEBUG,
        "django_ver": get_version(),
        "python_ver": os.environ["PYTHON_VERSION"],
        "nombre": analizador.nombre_proyecto,
        "grafico_listo": grafico_exitoso,
    }
    return render(request, "pages/home.html", context)
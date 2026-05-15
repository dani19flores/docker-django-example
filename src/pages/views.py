import io
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from django.conf import settings
from django.shortcuts import render
from django import get_version

class AnalizadorDemografico:
    def __init__(self):
        self.nombre_proyecto = "Fundamentos de Linux e Introducción a Django"
        self.public_dir = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'public'))
        self.csv_path = os.path.join(self.public_dir, 'SYB66_246_202310_Population Growth, Fertility and Mortality Indicators.csv')
        self.ruta_regplot = os.path.join(self.public_dir, 'images', 'grafico_dispersion.png')
        self.ruta_heatmap = os.path.join(self.public_dir, 'images', 'grafico_correlacion.png')

    def generar_graficos(self):
        try:
            print("--- RESTAURANDO LIMPIEZA MANUAL ---")
            
            # 1. PASO CLAVE: Limpieza manual de líneas (lo que sí funcionaba)
            with open(self.csv_path, 'r', encoding='latin1') as f:
                lineas = f.readlines()
            
            lineas_limpias = []
            for line in lineas:
                line = line.strip()
                # Quitamos ÚNICAMENTE la primera y última comilla de la línea
                if line.startswith('"') and line.endswith('"'):
                    line = line[1:-1]
                # Corregimos las comillas dobles internas
                line = line.replace('""', '"')
                lineas_limpias.append(line + '\n')
            
            # Convertimos a flujo de texto para Pandas
            contenido_limpio = io.StringIO("".join(lineas_limpias))

            # 2. CARGA: Ahora Pandas verá las comas correctamente
            # Saltamos 1 línea (el título T03...) y no usamos encabezado automático
            df = pd.read_csv(contenido_limpio, skiprows=1, header=None)
            
            # Asignamos las 7 columnas reales
            df.columns = ['Region', 'Name', 'Year', 'Series', 'Value', 'Footnotes', 'Source']
            print(f"DEBUG: Columnas detectadas: {len(df.columns)} (¡Debería ser 7!)")

            # 3. PROCESAMIENTO
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
            df_2020 = df[df['Year'] == 2020].copy()
            
            # Limpiar valores numéricos
            df_2020['Value'] = pd.to_numeric(df_2020['Value'].astype(str).str.replace(',', '', regex=True), errors='coerce')
            df_2020 = df_2020.dropna(subset=['Value'])

            # Tabla pivote
            df_pivot = df_2020.pivot_table(index='Name', columns='Series', values='Value')
            df_pivot.columns = [col.split(':')[0].strip() for col in df_pivot.columns]

            # --- GRÁFICA 1: REGPLOT ---
            col_mortalidad = [c for c in df_pivot.columns if 'Infant mortality' in c][0]
            col_esperanza = [c for c in df_pivot.columns if 'Life expectancy' in c][0]
            
            plt.figure(figsize=(10, 6))
            sns.regplot(data=df_pivot, x=col_mortalidad, y=col_esperanza, color='teal')
            plt.title('Mortalidad Infantil vs Esperanza de Vida (2020)')
            os.makedirs(os.path.dirname(self.ruta_regplot), exist_ok=True)
            plt.savefig(self.ruta_regplot)
            plt.close()

            # --- GRÁFICA 2: HEATMAP ---
            plt.figure(figsize=(12, 8))
            corr_matrix = df_pivot.corr()
            sns.heatmap(corr_matrix, annot=True, cmap='RdYlGn', fmt=".2f")
            plt.title('Matriz de Correlación (2020)')
            plt.tight_layout()
            plt.savefig(self.ruta_heatmap)
            plt.close()

            return True

        except Exception as e:
            import traceback
            print(f"ERROR DETALLADO:\n{traceback.format_exc()}")
            return False

def home(request):
    analizador = AnalizadorDemografico()
    # Asegúrate de llamar a la función en PLURAL
    graficos_exitosos = analizador.generar_graficos() 
    
    context = {
        "debug": settings.DEBUG,
        "django_ver": get_version(),
        "python_ver": os.environ.get("PYTHON_VERSION", "3.x"),
        "nombre": analizador.nombre_proyecto,
        "grafico_listo": graficos_exitosos
    }
    return render(request, "pages/home.html", context)
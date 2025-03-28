import itertools
import numpy as np
import pandas as pd
from collections import Counter
import time
import datetime

def calcula_lambda_y_r(num_tasks,num_items_X_task,num_items):
    """Calcula las condiciones lambda y r que deben satisfacer los diseños generados"""
    r=(num_tasks*num_items_X_task)//num_items
    lambd=r*(num_items_X_task-1)//(num_items-1)
    #print("r: ",r)
    #print("lambda: ",lambd)

    return r, lambd

def hace_conteos_de_one_way_frequencies(one_way_frequencies,item_count):
    """Agrega a los conteos totales de cada atributo en todas las versiones del diseño"""
    for key, value in item_count.items():
        #print(f"key {key}, {value}")
        one_way_frequencies[int(key)]+=value

    return one_way_frequencies

def hace_conteos_de_two_way_frequencies(tuplas_de_two_way_freq_matrix,pair_counts):
    """Agrega a los conteos totales de cada pareja de atributos en todas las versiones del diseño"""
    for pair, conteo in pair_counts.items():
        #print(f"key {pair}, {conteo}")
        i=int(list(pair)[0])-1
        j=int(list(pair)[1])-1
        elemento=(i,j,conteo)
        #print(elemento)
        tuplas_de_two_way_freq_matrix.append(elemento)
        #print(tuplas_de_two_way_freq_matrix)
    return tuplas_de_two_way_freq_matrix

def ejecutador_principal(num_items, num_tasks, num_items_x_task, num_versiones,seed):
    """Revisa que los inputs sean válidos y trata de ejecutar el generador principal"""

    if num_items<=0:
        print("Número total de ítems no puede ser <=0.")
    if num_tasks<=0:
        print("Número de tasks por versión no puede ser <=0.")
    if num_items_x_task<=0:
        print("Número de ítems por task no puede ser <=0.")
    if num_versiones<=0:
        print("Número de versiones no puede ser <=0.")
    if seed<=0 or seed>1000:
        print("La semilla del diseño experimental no puede ser <=0 ni >1.000.")

    # Genera num_versions versiones del diseño incompleto de bloques:
    conteo_de_versiones=0
    versiones_satisfacen=False
    while versiones_satisfacen==False:
        seed+=50
        total_versiones, r, lambda_val, error,one_way_frequencies, two_way_frequencies_matrix,versiones_satisfacen  = generate_multiple_versions(num_items, num_tasks, num_items_x_task, num_versiones,seed)
        conteo_de_versiones+=1
        print(f"Total versiones intentadas {conteo_de_versiones}.")

    if len(total_versiones)<num_versiones:
        print(f"Sólo se pudieron generar {len(total_versiones)} versión(es).")
    if error==True:
        print("El diseño no se ejecutó correctamente, revisar parámetros de diseño.")
    else:
        print("El diseño se ejecutó correctamente.")
    return(total_versiones,r,lambda_val,error,one_way_frequencies,two_way_frequencies_matrix,conteo_de_versiones)
    
def generate_multiple_versions(num_items, num_tasks, num_items_x_task, num_versions,seed):
    """Generate multiple versions of the BIBD with dynamic λ and r calculation. Nota: también calcula y muestra las frecuencias individuales de atributo y frecuencias de parejas en una matriz de num_items x num_items"""     
    
    one_way_frequencies={}
    for i in range(0,num_items):
        one_way_frequencies[i+1]=0     

    two_way_frequencies_matrix=np.array([[0]*num_items]*num_items)
    #print(two_way_frequencies_matrix)
    
    tuplas_de_two_way_freq_matrix=[]
    dict_de_tuplas_de_two_way_freq_matrix={}

    error=False
    versions = set()
    r, lambda_val = calcula_lambda_y_r(num_tasks,num_items_x_task,num_items)
    testeo_one_way_freq_total=num_versions*r
    
    rng = np.random.default_rng(seed=seed) # Utiliza la semilla provista por el usuario

    for version in range(num_versions):
        bibd = None
        attempts = 0
        seed+=100    # Para que la próxima versión se haga con una distinta aleatoriedad. Evita que se creen versiones iguales y el programa se caiga.
        rng = np.random.default_rng(seed=seed) # Regenera la aleatoriedad

        while bibd is None and attempts < 200:  # 100 reintentos se permiten
            generacion= generate_bibd(num_items, num_tasks, num_items_x_task, r, lambda_val,rng,one_way_frequencies,tuplas_de_two_way_freq_matrix)
            if generacion is not None:
                bibd = generacion[0]
                #print(bibd)
                attempts += 1   
        if bibd and bibd not in versions:
            versions.add(bibd)
            one_way_frequencies=generacion[1]
            
            # Aquí chequeamos que si hay una frecuencia individual pasada, de una vez descartar todas las versiones:
            for key,value in one_way_frequencies.items():
                if value>(testeo_one_way_freq_total+3):
                    print(f"Restricción de frecuencia individual violada en proceso de construcción de versiones con atributo {key} teniendo frecuencia {value}, regenerando...")
                    return versions,r,lambda_val,True,one_way_frequencies,two_way_frequencies_matrix,False

            #tuplas_de_two_way_freq_matrix.extend(generacion[2])
            for tupla in generacion[2]:
                pair=tupla[:2]
                #print(pair)
                if dict_de_tuplas_de_two_way_freq_matrix.get(pair) is not None:
                    dict_de_tuplas_de_two_way_freq_matrix[pair]+=tupla[2]           
                else:
                    dict_de_tuplas_de_two_way_freq_matrix[pair]=tupla[2]
            tuplas_de_two_way_freq_matrix=[]

            #print(f"Éxito generando la versión {version+1} en {datetime.datetime.now()}.")
        else:
            print(f"Warning: no se puede generar una versión {version+1} única después de 200 intentos. Los bloques que se intentaron generar no cumplen las condiciones de las ecuaciones que definen a (r, λ). Revisar parámetros de diseño.")
            print("Cancelando...")
            error=True
            break
   
    for key,value in one_way_frequencies.items():
        print(f"Atributo {key}: Freq {value}")
    
    for pair, value in dict_de_tuplas_de_two_way_freq_matrix.items():
        two_way_frequencies_matrix[pair[0]][pair[1]]+=value
        two_way_frequencies_matrix[pair[1]][pair[0]]+=value
    print(two_way_frequencies_matrix)

    versiones_satisfacen=valorar_version(r,lambda_val,num_items,num_tasks,num_items_x_task,one_way_frequencies,two_way_frequencies_matrix,num_versions)

    return versions,r,lambda_val,error,one_way_frequencies,two_way_frequencies_matrix,versiones_satisfacen

def generate_bibd(num_items, num_tasks, num_items_x_task, r, lambda_val,rng,one_way_frequencies,tuplas_de_two_way_freq_matrix):
    """Genera un Diseño de Bloques Incompleto (BIBD)."""
    max_intentos=10000
    items = list(range(1, num_items+1))

    all_combinations = list(itertools.combinations(items, num_items_x_task))
    #print(f"Número total posible de tasks distintos es {len(all_combinations)}.\n")

    for intento in range(max_intentos):
        selected_blocks = tuple(map(tuple, rng.choice(all_combinations, num_tasks, replace=False))) #ChatGPT dice que usar tuplas para guardar sets

        validacion_bibd=is_valid_bibd(selected_blocks,r, lambda_val,one_way_frequencies,tuplas_de_two_way_freq_matrix)
        #print(validacion_bibd)
        if isinstance(validacion_bibd, tuple):
            valido_bibd=validacion_bibd[0]
            one_way_frequencies=validacion_bibd[1]
            tuplas_de_two_way_freq_matrix=validacion_bibd[2]
            #print(validacion_bibd)
            if valido_bibd: # Si la condición lógica que es el primer output de is_valid_bibd se cumple, es porque el bloque es válido
                return selected_blocks,one_way_frequencies,tuplas_de_two_way_freq_matrix #,is_valid_bibd[2] # Se retorna el bloque válido generado, el conteo one-way de items y el conteo de parejas totales de items

    return None

def is_valid_bibd(blocks, r, lambda_val,one_way_frequencies,tuplas_de_two_way_freq_matrix):
    """Revisa si un bloque completo (el total de tasks en cada versión) satisface las condiciones de r  y lambda"""
    item_counts = Counter(item for block in blocks for item in block)
    pair_counts = Counter(frozenset(pair) for block in blocks for pair in itertools.combinations(block, 2))

    #condicion_de_satisfaccion=(all (count == r or count ==(r-1) or count ==(r+1) for count in item_counts.values()) and all(count_pair==lambda_val for count_pair in pair_counts.values()))
    condicion_de_satisfaccion=(all (count == r or count ==(r-1) or count ==(r+1) for count in item_counts.values()) and all(count_pair==lambda_val or count_pair==(lambda_val-1) or count_pair==(lambda_val+1) or count_pair==(lambda_val+2)  for count_pair in pair_counts.values()))
    #condicion_de_satisfaccion=(all (count == r or count ==(r+1) for count in item_counts.values()) and sum_pair_counts_igual_lambda>=num_pair_counts_minimos_igual_a_lambda)

    if condicion_de_satisfaccion:
        #print("uuuuu")
        one_way_frequencies=hace_conteos_de_one_way_frequencies(one_way_frequencies,item_counts)
        tuplas_de_two_way_freq_matrix=hace_conteos_de_two_way_frequencies(tuplas_de_two_way_freq_matrix,pair_counts)
        return condicion_de_satisfaccion,one_way_frequencies,tuplas_de_two_way_freq_matrix
    else:
        #print("falso falso")
        return condicion_de_satisfaccion

def valorar_version(r,lambda_val,num_items,num_tasks,num_items_x_task,one_way_frequencies,two_way_frequencies_matrix,num_versions):
    satisface=True
    
    # El número de veces teórico que aparece cada atributo en el one-way frequency:
    target_one_way_freq=(num_versions*num_tasks*num_items_x_task)//num_items
    
    # El lambda exacto nos dice el verdadero target de la tabla de two-way frequency:
    lambda_exact=r*(num_items_x_task-1)/(num_items-1)
    target_two_way_freq_total=round(lambda_val*num_versions,0)
    
    # Para cada one way frequency calcular si la max desviacion es 1
    for key,value in one_way_frequencies.items():
        if (value<=(target_one_way_freq+3)) and (value>=(target_one_way_freq-3)):
            satisface=True
            print(f"Condición de frecuencias individuales de {key}: frec {value} se cumple, (target de {target_one_way_freq})...")
        else:
            print(f"Condición de frecuencias individuales de {key}: frec {value} no se cumple, (target de {target_one_way_freq}), reintentando...")
            return False
    # Para cada two way frequency calcular si la maxima desviacion es 1
    for i in range(0,two_way_frequencies_matrix.shape[0]):
        for j in range(0,two_way_frequencies_matrix.shape[1]):
            if (i!=j) and (i>j):
                if (two_way_frequencies_matrix[i][j]<=(target_two_way_freq_total+4)) and (two_way_frequencies_matrix[i][j]>=(target_two_way_freq_total-4)):
                    print(f"Condición de frecuencias de parejas {i+1} y {j+1} se cumple (valor de {two_way_frequencies_matrix[i][j]}, target de {target_two_way_freq_total})")
                else:
                    print(f"Condición de frecuencias de parejas {i+1} y {j+1} no se cumple (valor de {two_way_frequencies_matrix[i][j]}, target de {target_two_way_freq_total}, reintentando...")
                    return False
    return True

def imprime_matriz(total_versiones):
    """Imprime cada versión generada del diseño"""
    for version_num, version in enumerate(total_versiones):
        print(f"\nVersión {version_num + 1}")
        for i, block in enumerate(version):
            print(f"Task {i+1}: {block}")
        input("Presione cualquier tecla para seguir...")

def guarda_matriz_en_xlsx(total_versiones,num_items_x_task,nom_cod_estudio,num_items,num_tasks,one_way_frequencies,two_way_frequencies_matrix):
    """Guarda el diseño en archivo xlsx."""

    # Se inicializa un dataframe vacío in versiones ni número de task y con todos los ítems en 0:
    matriz_completa=pd.DataFrame({"Versión":[],
                                  "Task":[]})
    for i in range(0,num_items_x_task):
        nom_col_item=f"Item_{i+1}"
        matriz_completa[nom_col_item]=[]
    
    # Se genera un dataframe por versión:
    for version_num, version in enumerate(total_versiones):
        # Se genera un dataframe vacío para cada versión de cuestionario
        matriz_temp=pd.DataFrame({"Versión":[0]*num_tasks,
                                  "Task":[0]*num_tasks})

        # Se llena la columna de tasks:
        for i in range(0,num_items_x_task):
            nom_col_item=f"Item_{i+1}"
            for j in range(0,num_tasks):
                matriz_temp.loc[j,nom_col_item]=version[j][i]
                if matriz_temp.loc[j,"Task"]==0:
                    matriz_temp.loc[j,"Task"]=j+1

        matriz_temp["Versión"]=version_num+1
        matriz_completa=pd.concat([matriz_completa,matriz_temp],ignore_index=True,axis=0)
    
    for column in matriz_completa.columns:
        matriz_completa[column].astype(int)
    
    one_way_frequencies_df=pd.DataFrame({'Frecuencia individual por atributo':one_way_frequencies})
    two_way_frequencies_matrix_df=pd.DataFrame(two_way_frequencies_matrix)
    two_way_frequencies_matrix_df.columns=[str(i) for i in range(1,num_items+1)]
    two_way_frequencies_matrix_df.index=[str(i) for i in range(1,num_items+1)]
    path=f"/home/rrodriguez/maxdiff_repo/MaxDiff/Repositorio_diseños/Proyecto-{nom_cod_estudio}.xlsx"

    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        matriz_completa.to_excel(writer,sheet_name='Matriz de diseño',index=False)
        one_way_frequencies_df.to_excel(writer,sheet_name='Frecuencias individuales',index=False)
        two_way_frequencies_matrix_df.to_excel(writer,sheet_name='Matriz de frecuencias',index=True)

    return


### Programa Principal: ###
""""
v = num_items = Número total de ítems.
b = num_tasks = número de tasks por versión.
k = num_items_x_task = número de ítems por task.
r = número de veces que aparece cada ítem en los b tasks en cada versión (calculado en def calcula_lambda_y_r, satisface la condición especificada en README.md)
lambda = número de veces que cada pareja posible de atributos aparece en el mismo task en cada versión (default=1) (calculado en def calcula_lambda_y_r, satisface la condición especificada en README.md)
num_versions = número de versiones, cada uno compuesto de b tasks.
seed = semilla para generar la aleatoriedad en la búsqueda de bloques.

Valores default para considerar como en los ITMs
num_items=13
num_tasks=8
num_items_x_task=5
num_versiones = 10
"""

nom_cod_estudio=input("Escriba el código o nombre del estudio: ")
num_items=int(input("Escriba número total de ítems (atributos a evaluar) en el diseño: "))

sug_num_items_x_task=False
while sug_num_items_x_task==False:
    num_items_x_task=int(input(f"Escriba el número de ítems por cada task presentado a encuestado. Se sugieren menos de {int(np.round(num_items/2,0))} ítems por task: "))
    
    # Ver en README.md por qué esto es un warning de diseño para el usuario:    
    if num_items_x_task>=(num_items/2):
        print("Warning: el número de ítems mostrados por task sería demasiado alto para el número total de ítems (>50%).\n")
        choice=input("Desea cambiar el número de ítems por task?(s/n): ")
        try:
            if choice=='s':
                num_items_x_task=int(input("Escriba el número de ítems por cada task presentado a encuestado: "))
                if num_items_x_task<=(num_items/2):
                    sug_num_items_x_task=True                  
            elif choice=='n':
                print("Warning: se sigue adelante con número más alto de lo recomendado para ítems por task.")
                sug_num_items_x_task=True
        except:
            print("Warning: se sigue adelante con número más alto de lo recomendado para ítems por task.")
            sug_num_items_x_task=True
    else:
        sug_num_items_x_task=True

# Esta sugerencia de Sawtooth verla también en el README.md
sug_num_tasks=False
sug_num_tasks_formula_sawtooth=3*num_items//num_items_x_task

while sug_num_tasks==False:
    num_tasks=int(input(f"Escriba el número total de tasks para mostrar por cada encuestado). Se sugieren {int(np.round(3*num_items/num_items_x_task,0))} tasks en total para mostrar a 1 encuestado: "))
    
    if num_tasks<sug_num_tasks_formula_sawtooth:
        print(f"Warning: se sugieren {sug_num_tasks_formula_sawtooth} tasks, en vez de {num_tasks}.\n")
        choice=input("Desea cambiar el número total de tasks para mostrar por encuestado?(s/n): ")
        try:
            if choice=='s':
                num_items_x_task=int(input("Escriba el número total de tasks para mostrar por cada encuestado): "))
                if num_tasks>sug_num_tasks_formula_sawtooth:
                    sug_num_tasks=True                  
            elif choice=='n':
                print("Warning: se sigue adelante con número más bajo de lo recomendado para número de tasks totales para mostrar a encuestado. Los estimados pueden salir mal.")
                sug_num_tasks=True
        except:
            print("Warning: se sigue adelante con número más bajo de lo recomendado para número de tasks totales para mostrar a encuestado. Los estimados pueden salir mal.")
            sug_num_tasks=True
    else:
        sug_num_tasks=True

num_versiones=int(input("Escriba número total de versiones para incluir en el cuestionario (default=10): "))
seed=int(input("Especifique la semilla para generar el diseño experimental (de 1 a 1.000): "))

start=time.time()
total_versiones,r, lambda_val,error,one_way_frequencies,two_way_frequencies_matrix,conteo_de_versiones = ejecutador_principal(num_items, num_tasks, num_items_x_task, num_versiones,seed)
timestamp=datetime.datetime.now()
end=time.time()
tiempo_ejecucion=np.round(end-start)

if error==False:
    print(f"Generación de diseño completadada en {tiempo_ejecucion} segundos. Total de diseños intentados es {conteo_de_versiones}")
    # imprime y guarda diseño:
    input("Presione cualquier tecla para imprimir el diseño y guardarlo en un xlsx:")
    #imprime_matriz(total_versiones)    
    guarda_matriz_en_xlsx(total_versiones,num_items_x_task,nom_cod_estudio,num_items,num_tasks,one_way_frequencies,two_way_frequencies_matrix)

    # Guarda diseño en log en un csv:
    log_nuevo=pd.DataFrame({"Código o id de proyecto":[nom_cod_estudio],
                        "Número total de ítems - v":[num_items],
                        "Número de tasks por versión - b":[num_tasks],
                        "Número de ítems por task - k":[num_items_x_task],
                        "Número de veces que cada ítem aparece por versión - r":[r],
                        "Número de veces que cada pareja de atributos aparece por versión":[lambda_val],
                        "Número de versiones":[num_versiones],
                        "Semilla":[seed],
                        "Timestamp de generación de diseño":[timestamp],
                        "Tiempo de ejecución":[tiempo_ejecucion]})
    
    log_nuevo.to_csv(f"/home/rrodriguez/maxdiff_repo/MaxDiff/Repositorio_diseños/Log_diseños.csv",mode='a',index=False,header=False)

    print(f"Diseño generado y exportado a /home/rrodriguez/maxdiff_repo/MaxDiff/Repositorio_diseños/Proyecto-{nom_cod_estudio}.xlsx. Entrada en el log en Log_diseños.csv con timestamp {timestamp} generada también.")

else:
    print("Cerrando el programa sin output de diseño ni log.")
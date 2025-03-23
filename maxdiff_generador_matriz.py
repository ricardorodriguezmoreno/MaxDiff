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
    print("r: ",r)
    print("lambda: ",lambd)

    return r, lambd

#def hace_conteos_de_one_way_frequencies(one_way_frequencies,item_count):
#    """Agrega a los conteos totales de cada atributo en todas las versiones del diseño"""
#    for key, value in item_count.values():
#        one_way_frequencies[int(key)]+=value

#    return one_way_frequencies

#def hace_conteos_de_two_way_frequencies(two_way_frequencies_matrix,bibd):
#    """Agrega a los conteos totales de cada pareja de atributos en todas las versiones del diseño"""
#    for num_task, task in enumerate(bibd):
#        for item in task:
#            two_way_frequencies_matrix    

#    return two_way_frequencies_matrix

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
    if seed<=0 or seed>9000:
        print("La semilla del diseño experimental no puede ser <=0 ni >9.000.")

    try:
        # Genera num_versions versiones del diseño incompleto de bloques:
        total_versiones, r, lambda_val, error = generate_multiple_versions(num_items, num_tasks, num_items_x_task, num_versiones,seed)

    except:
        print("Ocurrió una excepción, revisar código o parámetros de diseño.")

    else:
        if len(total_versiones)<num_versiones:
            print(f"Sólo se pudieron generar {len(total_versiones)} versión(es).")
        if error==True:
            print("El diseño no se ejecutó correctamente, revisar parámetros de diseño.")
        else:
            print("El diseño se ejecutó correctamente.")
        return(total_versiones,r, lambda_val,error)
    

def generate_multiple_versions(num_items, num_tasks, num_items_x_task, num_versions,seed):
    """Generate multiple versions of the BIBD with dynamic λ and r calculation. Nota: también calcula y muestra las frecuencias individuales de atributo y frecuencias de parejas en una matriz de num_items x num_items"""     
    
    one_way_frequencies={}
    for i in range(0,num_items):
        one_way_frequencies[i+1]=0

    two_way_frequencies_row=[0]*num_items
    two_way_frequencies_matrix=[two_way_frequencies_row]*num_items

    error=False
    versions = set()
    r, lambda_val = calcula_lambda_y_r(num_tasks,num_items_x_task,num_items)
    rng = np.random.default_rng(seed=seed) # Utiliza la semilla provista por el usuario

    for version in range(num_versions):
        bibd = None
        attempts = 0
        seed+=100    # Para que la próxima versión se haga con una distinta aleatoriedad. Evita que se creen versiones iguales y el programa se caiga.
        rng = np.random.default_rng(seed=seed) # Regenera la aleatoriedad

        while bibd is None and attempts < 200:  # 100 reintentos se permiten
            bibd = generate_bibd(num_items, num_tasks, num_items_x_task, r, lambda_val,rng)[0]
            print(bibd)
            attempts += 1   
        if bibd and bibd not in versions:
            versions.add(bibd)
            #one_way_frequencies=hace_conteos_de_one_way_frequencies(one_way_frequencies,bibd[1])
            #two_way_frequencies_matrix=hace_conteos_de_two_way_frequencies(two_way_frequencies_matrix,bibd)
            print(f"Éxito generando la versión {version+1}.")
        else:
            print(f"Warning: no se puede generar una versión {version+1} única después de 200 intentos. Los bloques que se intentaron generar no cumplen las condiciones de las ecuaciones que definen a (r, λ). Revisar parámetros de diseño.")
            print("Cancelando...")
            error=True
            break

    print(one_way_frequencies)
    input("xxxx")

    return versions, r, lambda_val,error,one_way_frequencies


def generate_bibd(num_items, num_tasks, num_items_x_task, r, lambda_val,rng):
    """Genera un Diseño de Bloques Incompleto (BIBD)."""
    max_intentos=5000
    items = list(range(1, num_items+1))

    all_combinations = list(itertools.combinations(items, num_items_x_task))
    #print(f"Número total posible de tasks distintos es {len(all_combinations)}.\n")

    for intento in range(max_intentos):
        selected_blocks = tuple(map(tuple, rng.choice(all_combinations, num_tasks, replace=False))) #ChatGPT dice que usar tuplas para guardar sets
        if is_valid_bibd(selected_blocks,r, lambda_val): # Si la condición lógica que es el primer output de is_valid_bibd se cumple, es porque el bloque es válido
            print("asd")
            return selected_blocks #,is_valid_bibd[1],is_valid_bibd[2] # Se retorna el bloque válido generado, el conteo one-way de items y el conteo de parejas totales de items

    return None


def is_valid_bibd(blocks, r, lambda_val):
    """Revisa si un bloque completo (el total de tasks en cada versión) satisface las condiciones de r  y lambda"""
    item_counts = Counter(item for block in blocks for item in block)
    pair_counts = Counter(frozenset(pair) for block in blocks for pair in itertools.combinations(block, 2))

    num_pair_counts_minimos_igual_a_lambda=int(0.8*len(pair_counts)) # modificar este 0.9 para hacer más o menos exigente el cumplimiento de la condición lambda.
    sum_pair_counts_igual_lambda=0
    for count_pair in pair_counts.values():
        if count_pair==lambda_val:
            sum_pair_counts_igual_lambda+=1    

    #print(f"Conteo de lambdas:{sum_pair_counts_igual_lambda}\n")
    print(f"Conteo de items tests: {item_counts}")
    #print(f"Conteo de pair tests: {pair_counts}\n")

    print(f"{all (count == r or count ==(r-1) or count ==(r+1) for count in item_counts.values())}\n")
    #print(sum_pair_counts_igual_lambda>=num_pair_counts_minimos_igual_a_lambda)

    return all (count == r or count ==(r-1) or count ==(r+1) for count in item_counts.values()) and sum_pair_counts_igual_lambda>=num_pair_counts_minimos_igual_a_lambda # Menos exigente en el one-way balance
    #return (all (count == r or count ==(r-1) or count ==(r+1) for count in item_counts.values()) and sum_pair_counts_igual_lambda>=num_pair_counts_minimos_igual_a_lambda),item_counts,pair_counts # Menos exigente en el one-way balance
    #return (all (count == r or count ==(r+1) for count in item_counts.values()) and sum_pair_counts_igual_lambda>=num_pair_counts_minimos_igual_a_lambda),item_counts,pair_counts # Más exigente en el one-way balance


def imprime_matriz(total_versiones):
    """Imprime cada versión generada del diseño"""
    for version_num, version in enumerate(total_versiones):
        print(f"\nVersión {version_num + 1}")
        for i, block in enumerate(version):
            print(f"Task {i+1}: {block}")
        input("Presione cualquier tecla para seguir...")


def guarda_matriz_en_xlsx(total_versiones,num_items_x_task,nom_cod_estudio,num_items,num_tasks):
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
    
    matriz_completa.to_excel(f"/home/rrodriguez/maxdiff_repo/Repositorio_diseños/Proyecto-{nom_cod_estudio}.xlsx",index=False)
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
                if num_items_x_task>=(num_items/2):
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
                if num_tasks<sug_num_tasks_formula_sawtooth:
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
seed=int(input("Especifique la semilla para generar el diseño experimental (de 1 a 9.000): "))

start=time.time()
total_versiones,r, lambda_val,error = ejecutador_principal(num_items, num_tasks, num_items_x_task, num_versiones,seed)
timestamp=datetime.datetime.now()
end=time.time()

if error==False:
    print(f"Generación de diseño completadada en {np.round(end-start)} segundos.")

    # imprime y guarda diseño:
    input("Presione cualquier tecla para imprimir el diseño y guardarlo en un xlsx:")
    #imprime_matriz(total_versiones)    
    guarda_matriz_en_xlsx(total_versiones,num_items_x_task,nom_cod_estudio,num_items,num_tasks)

    # Guarda diseño en log en un csv:
    log_nuevo=pd.DataFrame({"Código o id de proyecto":[nom_cod_estudio],
                        "Número total de ítems - v":[num_items],
                        "Número de tasks por versión - b":[num_tasks],
                        "Número de ítems por task - k":[num_items_x_task],
                        "Número de veces que cada ítem aparece por versión - r":[r],
                        "Número de veces que cada pareja de atributos aparece por versión":[lambda_val],
                        "Número de versiones":[num_versiones],
                        "Semilla":[seed],
                        "Timestamp de generación de diseño":[timestamp]})
    
    log_nuevo.to_csv(f"/home/rrodriguez/maxdiff_repo/Repositorio_diseños/Log_diseños.csv",mode='a',index=False,header=False)

    print(f"Diseño generado y exportado a /home/rrodriguez/maxdiff_repo/Repositorio_diseños/Proyecto-{nom_cod_estudio}.xlsx. Entrada en el log en Log_diseños.csv con timestamp {timestamp} generada también.")

else:
    print("Cerrando el programa sin output de diseño ni log.")
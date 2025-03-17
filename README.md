# MaxDiff
##Implementación de MaxDiff - generación de matriz de preguntas y procesamiento de resultados

###Diseño experimental: Usa el Diseño de Bloques Balanceado Incompleto, con las siguientes variables que introduce el usuario:

**v =** Número total de ítems.
**b =** número de tasks por set.
**k =** número de ítems por task.
**r =** número de veces que aparece cada ítem en los b tasks en un set dado.
**lambda =** número de veces que cada pareja posible de atributos aparece en el mismo task en un set dado.

No se implementan prohibiciones de atributos presentados en la misma task ni set.

Se satisfacen las siguientes condiciones:


El objetivo es que los datos procesados luego se procesen con HB (hierarchical Bayer)

###Implementación en Python:
Usa librerías Numpy, Pandas, Combinations de itertools, collections de Counter. **Ver archivo requirements.txt**.


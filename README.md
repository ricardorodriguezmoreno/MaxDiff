# MaxDiff
## Implementación de MaxDiff - generación de matriz de preguntas y procesamiento de resultados

### Diseño experimental: 
Usa el Diseño de Bloques Balanceado Incompleto, con las siguientes variables que introduce el usuario:

**v =** Número total de ítems.\
**b =** número de tasks por set.\
**k =** número de ítems por task.\
**r =** número de veces que aparece cada ítem en los b tasks en un set dado.\
**lambda =** número de veces que cada pareja posible de atributos aparece en el mismo task en un set dado.

No se implementan prohibiciones de atributos presentados en la misma task ni set.

Se satisfacen las siguientes condiciones:

![image](https://github.com/user-attachments/assets/d5faa35b-871a-4ca3-8627-1e3cee6cc4c9)

La primera ecuación es una constante para el número de veces que aparece cada atributo.\
La segunda ecuación es una contante para el número de veces que aparece cada pareja de atributos.

El objetivo es que los datos procesados luego se procesen con HB (hierarchical Bayer)


Number of Items per Task (Question)     

Generally, we recommend displaying either four or five items at a time (per set or question) in MaxDiff questionnaires. However, we do not recommend displaying more than half as many items as there are items in your study. Therefore, if your study has just eight total items, we would not recommend displaying more than four items per set.     

Number of Task (Questions) per Respondent     

If using HB to estimate individual-level scores, we generally recommend asking as many Task (questions) per respondent such that each item has the opportunity to appear from three to five times per respondent. For example, consider a study with 20 items where we are displaying four items per set. With 20 total sets, we know that each item will be displayed 4 times (assuming the design is perfectly balanced). This leads to the following decision rule and formula:     

 For best results (under HB estimation), the suggested number of Tasks is at least:      
 
$3K / k$  

Where K is the total number of items in the study, and k is the number of items displayed per Task.     

**The software will warn you if the number of sets you have requested leads to each item being displayed fewer than 2 times per respondent.* *

These recommendations assume HB estimation.


NOTA LA LIBRERIA OPENPYL SE INSTALO PERO NO SE USA, ANOTARLO POR ACÁ
LO MISMO LA LIBRERIA xlsxwriter

### Implementación en Python:
Usa librerías Numpy, Pandas, Combinations de itertools, collections de Counter. **Ver archivo requirements.txt**.


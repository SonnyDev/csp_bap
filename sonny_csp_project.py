"""Resolution du problème d'allocation des postes à quai.
    Nous utilisons le solveur CP-SAT inclus dans OR-Tools.
    Pour l'installer sur l'environnement Python : !pip install ortools
"""
import re
# Importation de la classe cp_model
from ortools.sat.python import cp_model

"""Cette méthode permet de récupérer les données contenues dans les fichiers et de les
retourner sous forme d'une matrice"""


def get_data(f_navires, f_postes):
    # Matrice vide pour stocker les données
    data = []
    navires = []
    postes = []

    # Ignorer la première ligne de chaque fichier
    next(f_navires)
    next(f_postes)

    # Lire les données de navires.csv
    for line in f_navires:
        # Retirer le caractère de fin de ligne (\n)
        line = line.strip()
        # Diviser la ligne en colonnes en utilisant la virgule comme séparateur
        colonnes = line.split(',')
        colonnes = [int(col) for col in colonnes]
        # Ajouter la ligne sous forme d'une liste à la matrice data
        navires.append(colonnes)

    for line in f_postes:
        # Retirer le caractère de fin de ligne (\n)
        line = line.strip()
        # Extraire les types de navires supportés de la colonne 2 à l'aide d'une expression régulière
        expression = r'\[(\d+(?:, ?\d+)*)\]'
        resultat = re.search(expression, line)
        types_navires = [int(x) for x in resultat.group(1).split(',')]
        # Diviser les autres colonnes en utilisant la virgule comme séparateur
        colonnes = line.split(',')
        # Convertir les données en entiers et remplacer la colonne des types de navires par la liste extraite
        colonnes = [int(colonnes[0]), int(colonnes[1]), types_navires, int(colonnes[5])]
        # Ajouter la ligne sous forme d'une liste à la matrice postes
        postes.append(colonnes)
    data.append(navires)
    data.append(postes)
    # Retourner la matrice contenant les données
    return data


"""Méthode principale du programme. Etant donnés les noms de deux fichiers csv
    contenant les informations sur les navires et les postes à quai et situés au meme
    emplacement que le programmme, la méthode renvoie une allocation d'un poste à quai
    pour chaque navire. """


def main():
    with open('navires.csv', 'r') as f_navires, open('postes.csv', 'r') as f_postes:
        data = get_data(f_navires, f_postes)
        navires = data[0]
        postes = data[1]
        # Les paramètres n = nombre de navires, p= nombres de postes et t=horizon
        n = len(navires)
        p = len(postes)
        t = 150

    # Modèle
    model = cp_model.CpModel()

    # Variables
    x = {}
    for navire in range(n):
        for poste in range(p):
            # Variable x[i, k] = 1, si le poste k est alloué au navire i, 0 sinon
            x[navire, poste] = model.NewBoolVar(f'x[{navire},{poste}]')
    a = {}
    d = {}
    for navire in range(n):
        # Variables a[i] = Temps d'accostage du navire i
        a[navire] = model.NewIntVar(0, t, f'a[{navire}]')

        # Variables d[i] = Temps de départ du navire i
        d[navire] = model.NewIntVar(0, t, f'd[{navire}]')

    # Contraintes
    # 1. le temps de départ = temps d'accostage + durée du traitement du navire
    for navire in range(n):
        model.Add(d[navire] == a[navire] + int(navires[navire][3]))

    # 2. Chaque navire reçoit exactement 1 poste à quai.
    for navire in range(n):
        model.AddExactlyOne(x[navire, poste] for poste in range(p))

    # 3. Chaque poste à quai est alloué à 0 ou plusieurs navires
    for poste in range(p):
        model.AddAtLeastOne(x[navire, poste] for navire in range(n))

    # Contraintes techniques sur la longueur, le tirant d'eau et les types de navires
    for i in range(n):
        for k in range(p):
            model.AddImplication(x[i, k], navires[i][1] <= postes[k][1])
            model.AddImplication(x[i, k], navires[i][2] <= postes[k][3])
            model.AddImplication(x[i, k], navires[i][4] in postes[k][2])

    # Résolution du problème
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Affichage de solution.
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for navire in range(n):
            for poste in range(p):
                if solver.BooleanValue(x[navire, poste]):
                    print(
                        f'Navire {navire} est alloué au poste {poste}. Arrivée {solver.Value(a[navire])}, Depart {solver.Value(d[navire])}')
    else:
        print('Pas de solution.')


if __name__ == '__main__':
    main()

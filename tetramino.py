from getkey import getkey
import sys
import os
""" Auteur: LIEFFERINCKX Romain
Date de remise: 17/12/2023
Nom du projet: tetramino
Le but de ce code est de recréer le jeu de société Tétraminos en python.
En utilisant des fichiers textes pour se servir des données qu'ils contiennent a fin de créer le plateau de jeu et 
les tétraminos.
Il a fallu utiliser getkey.py de sorte a ne pas devoir appuyer sur enter a chaque coup joué.
"""

def create_grid(w: int, h: int):
    """fonction: create_grid:
        fonction qui crée une matrice qui sera notre plateau de jeu et crée le carré du centre ou l'on placera les
        tétraminos.
        Arguments:
        -w (int): largeur du plateau
        -h (int): hauteur du plateau
        Return:
        -matrice (liste de liste)
    """
    matrice = [["  "] * ((w * 3) + 2) for _ in range((h * 3) + 2)]  # construction de la matrice avec des espaces
    for j in range(h, h + h + 2, h + 1):  # construction du carré central
        for k in range(w + 1, w + 6):
            matrice[j][k] = '--'
    for l in range(h + 1, h + h + 1):
        for m in range(w, w + 1):
            matrice[l][m] = ' |'
    for n in range(h + 1, h + h + 1):
        for o in range(w + w + 1, w + w + 2, w + 1):
            matrice[n][o] = '| '
    return matrice


def import_card(file_path):
    """fonction: import_card:
        fonction qui importe les éléments d'un fichier (carte_(...).txt).
        Arguments:
        - file_path: chemin du fichier (carte_(...).txt)
        Return:
        - (tuple(x, y), list(tetramino)) → Tuple contenant les dimensions du plateau (sous forme d’un tuple (x, y)),
         ainsi qu’une liste de tetraminos
    """
    with open(file_path) as info_carte:  # ouvre le fichier (carte_(...))
        elem_carte = info_carte.readlines()  # lit les données du fichier
        taille = tuple(map(int, elem_carte.pop(0).strip("\n").split(", ")))  # tuple d'entier qui représente la taille
        # du plateau de jeu
        for texte in range(len(elem_carte)):
            elem_carte[texte] = elem_carte[texte].strip("\n").split(";;")  # quand il y a ;; je sépare le texte
            elem_carte[texte][0] = [tuple(map(int, i.strip("()").split(", "))) for i in elem_carte[texte][0].split(";")]
            # convertit les coordonnées des tétraminos en tuples d'entiers
            elem_carte[texte].append((0, 0))  # ajout de (0,0) comme tuple de position initial
    return taille, elem_carte


def setup_tetraminos(tetraminos, grid):
    """ fonction: setup_tetraminos:
        Mets en place les tétraminos importés depuis le fichier chacun dans leur sous-matrice sur la matrice principale.
         Cette fonction est appelée une seule fois en début de jeu pour initialiser la grille de départ.
         Arguments:
         -tetraminos
         -grid
        Return:
        -(list(list), list(tetramino)) → Nouvelle grille avec les tetraminos placés,
         et la liste de tétra- minos avec leur nouvelle position mise à jour.
    """
    h = (len(grid) - 2) // 3
    w = (len(grid[0]) - 2) // 3
    liste_pos_depart = [(0, 0), (w + 1, 0), (2 * w + 2, 0), (0, h + 1), (2 * w + 2, h + 1),
                        (0, 2 * h + 2), (w + 1, 2 * h + 2), (2 * w + 2, 2 * h + 2)]  # Positions de départ pour
    # chaque tétramino
    for i in range(len(tetraminos)):
        tetraminos[i][2] = liste_pos_depart[i]
    for tetramino in tetraminos:  # donne les positions de départ à chaque tétramino
        for coord in tetramino[0]:
            x, y = int(coord[0] + tetramino[2][0]), int(coord[1] + tetramino[2][1])
            code_couleur = "\x1b[{}m{} \x1b[0m".format(tetramino[1], tetraminos.index(tetramino) + 1)  # donne la
            # couleur des tétraminos
            grid[y][x] = code_couleur
    return grid, tetraminos


def place_tetraminos(tetraminos, grid):
    """ fonction: place_tetraminos:
        Place les tétraminos sur la grille donnée. Cette fonction sert à effectuer un déplacement à tout moment du jeu.
        Arguments:
        -tetraminos
        -grid
        Return:
        -list(list) → Nouvelle grille avec les tetraminos placés
    """
    grid = create_grid((len(grid[0]) - 2) // 3, (len(grid) - 2) // 3)  # création nouvelle grille
    # pour ne pas modier l'originale
    for tetramino in tetraminos:
        for coord in tetramino[0]:
            x, y = (int(coord[0]) + int(tetramino[2][0])), int(coord[1] + tetramino[2][1])  # place les tétraminos
            # sur la grille
            if 0 <= x < len(grid[0]) and 0 <= y < len(grid) and grid[y][x] == "  ":  # mise en place des conditions de
                # placement des tétraminos
                code_couleur = "\x1b[{}m{} \x1b[0m".format(tetramino[1], tetraminos.index(tetramino) + 1)
                grid[y][x] = code_couleur
            else:  # Si les coordonnées ne sont pas valides, affichage du tétramino avec "XX"
                code_couleur = "\x1b[{}m{}\x1b[0m".format(tetramino[1], "XX")
                grid[y][x] = code_couleur
    return grid


def rotate_tetramino(tetramino, clockwise=True):
    """ fonction: rotate_tetramino:
        Permet d’effectuer la rotation du tetramino. Pour effectuer la rotation, seul le premier élément du tetramino,
         ses coordonnées initiales, est modifié. Attention à ne pas utiliser la position incrémentée par le décalage.
         Arguments:
         - tetramino
         -clockwise
        Return:
        -tetramino → Tetramino avec les coordonnées initiales modifiée par la rotation.
    """

    def rotate_point(x, y):
        return (-y, x) if clockwise else (y, -x)  # change les x et y du tétramino dans le sens des aiguille
        # d'une montre ou pas

    coord_post_rotation = [rotate_point(x, y) for x, y in tetramino[0]]  # applique le changement
    tetramino[0] = coord_post_rotation
    return tetramino


def check_move(tetramino, grid):
    """ fonction: check_move:
        Vérifie si la position actuelle du tétramino est valide (celui-ci ne chevauche pas une autre pièce
        ou une bordure).
        Arguments:
        -tetramino
        -grid
        Return:
        -bool → True si la position actuelle est valide, False autrement.
    """
    res = True
    for x, y in tetramino[0]:
        x, y = int(x + tetramino[2][0]), int(y + tetramino[2][1])
        if "XX" in grid[y][x]:  # Vérification si la coordonnée du tétramino est valide
            res = False
    return res


def check_win(grid):
    """ fonction: check_win:
        Vérifie si la position actuelle des pièces correspond à une configuration gagnante.
        Arguments:
        -grid
        Return:
        -bool → True si la configuration est gagnante, False autrement.
    """
    res = True
    for ligne in range((len(grid) - 2) // 3, (((len(grid) - 2) // 3) * 2) + 1):  # parcourt la zone centrale
        for colonne in range((len(grid[0]) // 3) + 1, ((len(grid[0]) // 3) * 2) + 1):
            if "  " in grid[ligne][colonne]:  # vérifie la condition de victoire
                res = False
    return res


def print_grid(grid, no_number=False):
    """ fonction: print_grid:
        Print le plateau de jeu.
        Pour améliorer la jouabilité,
        les limites du plateau doivent être affichées en utilisant les caractères ’|’ (bordures verticales)
        et (-) (bordures horizontales). Référez-vous aux figures des sections précédentes
        pour un exemple (par exemple : Figure 1). Le paramètre no_number indique si les pièces doivent être affichées
        avec (si sa valeur est False) ou sans (si sa valeur est True) les chiffres correspondants.
        Arguments:
        -grid
        -no_number
        Return:
        -None
    """
    for pos in range(2 * len(grid[0]) + 1):
        print("-", end="")
    print("-")
    for ligne in grid:
        print("|", end="")
        for case in ligne:
            texte_print = list(case)
            if no_number and texte_print[0] == "\x1b" and "XX" not in case:  # no number -> les tétraminos
                # avec ou sans chiffres dedans
                texte_print[-6] = " "
            print("".join(texte_print), end="")
        print("|")
    for pos in range(2 * len(grid[0]) + 1):
        print("-", end="")
    print("-")


def verif_bords(tetramino, grid):
    """fonction: verif_bords:
     fonction qui vérifie si le tétramino sort du cadre de jeu
    Arguments:
     -tetramino:
     -grid:
     return:
      -booléen
    """
    res = True
    for x, y in tetramino[0]:
        x, y = int(x + tetramino[2][0]), int(y + tetramino[2][1])
        if x < 0 or x >= len(grid[0]) or y < 0 or y >= len(grid):  # Vérifie si les coordonnées sont dans
            # le cadre de jeu
            res = False
    return res


def main():
    """ fonction: main:
        Gère le déroulement du jeu. Main est la fonction principale qui sera appellée au lancement du programme,
         et se terminera à la fin de la partie.
         Arguments:
         None
        Return:
        -bool → True une fois la partie gagnée.
    """
    global etat_de_la_partie_2
    if len(sys.argv) != 2:  # utilisation de sys pour pouvoir utiliser la console pour la gestion des arguments
        # en ligne de commande
        # exemple: python tetramino.py carte_1.txt
        sys.exit(1)
    file_path = sys.argv[1]
    try:
        taille, tetraminos = import_card(file_path)
    except FileNotFoundError:
        print("Fichier non existant")
        sys.exit(1)
    grille, tetraminos = setup_tetraminos(tetraminos, create_grid(*taille))  # mise en place de la grille
    # et des tétraminos
    numéros_tétraminos = []
    commande_jeu = ['O', 'U', 'I', 'J', 'K', 'L', 'V']
    for i in range(len(tetraminos)):
        numéros_tétraminos.append(i)
    etat_de_la_partie = 1
    while etat_de_la_partie == 1:  # boucle qui continue tant que le jeu n'est pas gégné
        if os.name == 'posix':
            os.system('clear')
        else:
            os.system('cls')
        print_grid(grille, no_number=False)
        try:  # try exceptnpour qu'il n'y ait aucun crash si le coup joué n'est pas valable
            coup_entrer = getkey()
        except Exception as e:
            print(f"Erreur lors de la saisie clavier : {e}")
            coup_entrer = None
        if coup_entrer:
            if coup_entrer.isdigit():
                coup_entrer = int(coup_entrer) - 1
                while coup_entrer not in numéros_tétraminos:
                    print("Veuillez entrer le numéro d'un tétramino sur le plateau: ")
                    try:
                        coup_entrer = getkey()
                    except Exception as e:
                        coup_entrer = None
                    if coup_entrer:
                        if coup_entrer.isdigit():
                            coup_entrer = int(coup_entrer) - 1
                etat_de_la_partie_2 = True
            else:
                etat_de_la_partie_2 = False

        while etat_de_la_partie_2:  # boucle 2 qui va permettre l'actualisation du plateau de jeu
            if os.name == 'posix':
                os.system('clear')
            else:
                os.system('cls')
            print_grid(grille, no_number=True)
            tetramino_selectionne = tetraminos[coup_entrer].copy()
            place_tetraminos([tetramino_selectionne], grille)
            coup_entrer_2 = getkey()
            while coup_entrer_2.upper() not in commande_jeu:
                coup_entrer_2 = getkey()
            coup_entrer_2 = coup_entrer_2.upper()
            if coup_entrer_2 == 'O':
                tetramino_selectionne = rotate_tetramino(tetramino_selectionne, True)  # opère la rotation
                # dans le sens horaire si la condition est respectée
                if not verif_bords(tetramino_selectionne, grille):  # vérifie la condition
                    tetramino_selectionne = rotate_tetramino(tetramino_selectionne, False)
            elif coup_entrer_2 == 'U':
                tetramino_selectionne = rotate_tetramino(tetramino_selectionne, False)  # opère la rotation
                # dans le sens anti horaire si la condition est respectée
                if not verif_bords(tetramino_selectionne, grille):  # vérifie la condition
                    tetramino_selectionne = rotate_tetramino(tetramino_selectionne, True)
            elif coup_entrer_2 == 'I':
                tetramino_selectionne_copy = tetramino_selectionne.copy()
                tetramino_selectionne_copy[2] = (tetramino_selectionne[2][0], tetramino_selectionne[2][1] - 1)
                if verif_bords(tetramino_selectionne_copy, grille):  # si la condition est respectée
                    # le tétramino est déplacé
                    tetramino_selectionne = tetramino_selectionne_copy
            elif coup_entrer_2 == 'J':
                tetramino_selectionne_copy = tetramino_selectionne.copy()
                tetramino_selectionne_copy[2] = (tetramino_selectionne[2][0] - 1, tetramino_selectionne[2][1])  # si la
                # condition est respectée le tétramino est déplacé
                if verif_bords(tetramino_selectionne_copy, grille):
                    tetramino_selectionne = tetramino_selectionne_copy
            elif coup_entrer_2 == 'K':
                tetramino_selectionne_copy = tetramino_selectionne.copy()
                tetramino_selectionne_copy[2] = (tetramino_selectionne[2][0], tetramino_selectionne[2][1] + 1)
                if verif_bords(tetramino_selectionne_copy, grille):
                    tetramino_selectionne = tetramino_selectionne_copy
            elif coup_entrer_2 == 'L':
                tetramino_selectionne_copy = tetramino_selectionne.copy()
                tetramino_selectionne_copy[2] = (tetramino_selectionne[2][0] + 1, tetramino_selectionne[2][1])
                if verif_bords(tetramino_selectionne_copy, grille):
                    tetramino_selectionne = tetramino_selectionne_copy
            elif coup_entrer_2 == 'V':
                etat_de_la_partie_2 = not check_move(tetramino_selectionne, grille) # si la condition est respectée le
                # tétramino est placé
            tetraminos[coup_entrer] = tetramino_selectionne
            grille = place_tetraminos(tetraminos, grille)
            if os.name == 'posix':
                os.system('clear')
            else:
                os.system('cls')
            print_grid(grille, no_number=False)
        if check_win(grille):  # si la condition est respectée la partie est finie et le joueur a gagné
            etat_de_la_partie = 0
            print("Félicitations! Vous avez gagné!")


if __name__ == "__main__":
    main()

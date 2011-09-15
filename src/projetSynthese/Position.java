package projetSynthese;

/**
 * classe position servant a representer une coordonnee sur l'echiquier.
 * 
 * @author Francois Allard
 */
public class Position {
	/**
	 * Numero de la ligne
	 */
	private int ligne; 
	/**
	 * Numero de la colonne
	 */
	private int colonne; 

	/*
	 * Le numero de colonne corrspondant à la coordonnées X et le numero de
	 * ligne à la coordonnées Y, je trouve plus naturel d'inscrire les positions
	 * avec une notation X,Y. J'ai donc inverser ces deux paramètres.
	 */
	/**
	 * Constructeur de la classe position, sert a initialiser les deux parametre
	 * d'une position, sa ligne et sa colonne
	 * 
	 * @param prend
	 *            en parametre le numero de colonne de la position
	 * @param prend
	 *            en parametre le numero de ligne de la position
	 */
	public Position(int colonne, int ligne) {
		this.ligne = ligne;
		this.colonne = colonne;
	}

	public int getLigne() {
		return ligne;
	}

	public int getColonne() {
		return colonne;
	}

	public void setLigne(int ligne) {
		this.ligne = ligne;
	}

	public void setColonne(int colonne) {
		this.colonne = colonne;
	}

	public boolean equals(Position position) {
		return position.getColonne() == this.getColonne()
				&& position.ligne == this.ligne;
	}

}
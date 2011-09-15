package projetSynthese;

/**
 * classe Case servant a representer une case d'un jeu d'echec
 * 
 * @author Francois Allard
 */

public class Case {
	/**
	 * Piece contenu par la case
	 */
	private Piece piece;
	
	/**
	 * Constructeur par defaut
	 */
	public Case()
	{
		
	}
	
	/**
	 * Constructeur parametre
	 * @param Prend en parametre la piece qu'il y aura sur la case
	 */
	public Case(Piece piece)
	{
		this.piece = piece;
	}
	
	/**
	 * Methode get piece, retourne la piece qui se trouve sur la case, ou null si la case est vide
	 * @return Piece sur la case
	 */
	public Piece getPiece() {
		return piece;
	}
	
	/**
	 * Methode set piece, met un objet Piece sur la case
	 * @param Piece ˆ placer
	 */
	public void setPiece(Piece piece) {
		this.piece = piece;
	}
	
	/**
	 * Methode estOccupe servant a savoir si la case est occupe ou non.
	 * @return Boolean
	 */
	public boolean estOccupe()
	{
		return (piece != null);	
	}
	
	/**
	 * Methode estOccupe servant a savoir si la case est occupe ou non d'une piece d'une couleur entrer en parametre.
	 * @return Boolean
	 * @param String
	 */
	public boolean estOccupe(String couleur)
	{
		if (piece == null)
			return false;
		else
			return (piece.getCouleur().equals(couleur));
	}
	
}

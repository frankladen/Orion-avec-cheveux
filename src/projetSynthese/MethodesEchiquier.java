package projetSynthese;
/**
 * Interface contenant les prototype des methodes que devra implementer un echiquier
 * 
 * @author Francois Allard
 */
public interface MethodesEchiquier 
{
	
	public abstract void debuter();
	public abstract Case getCase(int ligne, int colonne);
	public abstract boolean cheminPossible (Deplacement deplacement);
	public abstract boolean captureParUnPionPossible(Deplacement deplacement);
}

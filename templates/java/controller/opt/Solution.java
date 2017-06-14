public class Program {

    public int add(int debt, int prize) {
        if (debt > Integer.MAX_VALUE - prize) {
          return debt;
        } else {
          return debt+prize;
        }
    }
}

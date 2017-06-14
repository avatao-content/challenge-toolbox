import static org.junit.Assert.assertEquals;
import org.junit.Test;

public class ProgramTest {

  @Test
  public void notOverflow() {
    Program adder = new Program();
    int value1 = Integer.MAX_VALUE-1;
    int value2 = 1;
    int result = adder.add(value1, value2);
    assertEquals(Integer.MAX_VALUE, result);
  }

  @Test
  public void isOverflow() {
    Program adder = new Program();
    int value1 = Integer.MAX_VALUE-100;
    int value2 = 101;
    int result = adder.add(value1, value2);
    assertEquals(Integer.MAX_VALUE-100, result);
  }
}

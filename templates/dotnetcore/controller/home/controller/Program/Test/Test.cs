using Xunit;
using App;

namespace UnitTests
{
    public class Test
    {
        [Fact]
        public void CorrectHello()
        {
            Assert.Equal("Hello, World!!", Program.hello());
        }

        [Fact]
        public void AnotherCorrectHello()
        {
            Assert.Equal("Hello, World!!", Program.hello());
        }
    }
}

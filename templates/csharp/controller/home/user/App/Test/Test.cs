using NUnit.Framework;
using System;

namespace App
{
	[TestFixture ()]
	public class Test
	{

		[Test]
		public void Test_Add_Numbers()
		{
			int result = MainClass.Add(4, 4);
			Assert.AreEqual(8, result);
		}

		[Test]
		public void Test_Add_Zeros()
		{
			int result = MainClass.Add(0, 0);
			Assert.AreEqual(0, result);
		}

		[Test]
		public void Test_Print()
		{
			string result = MainClass.Print("asdf");
			Assert.AreEqual("asdf", result);
		}

	}
}


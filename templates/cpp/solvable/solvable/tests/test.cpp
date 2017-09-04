#include <cmath>
#include "gtest/gtest.h"
#include "geomean.cpp"

TEST(GeoMeanTest, OneInt) {
	EXPECT_DOUBLE_EQ(1.0, geometric_mean(1));
	EXPECT_DOUBLE_EQ(-1.0, geometric_mean(-1));
	EXPECT_DOUBLE_EQ(42.0, geometric_mean(42));
	EXPECT_DOUBLE_EQ(200000.0, geometric_mean(200000));
}

TEST(GeoMeanTest, TwoInts) {
	EXPECT_DOUBLE_EQ(2.0, geometric_mean(1, 4));
	EXPECT_TRUE(std::isnan(geometric_mean(1, -4)));
	EXPECT_NEAR(6.48074069, geometric_mean(6, 7), 0.00000001);
	EXPECT_NEAR(4221.15671350, geometric_mean(42, 424242), 0.00000001);
}

TEST(GeoMeanTest, OneIntOneFloat) {
	EXPECT_DOUBLE_EQ(2.0, geometric_mean(1, 4.0f));
	EXPECT_TRUE(std::isnan(geometric_mean(1.0f, -4)));
	EXPECT_NEAR(6.48074069, geometric_mean(6, 7.0f), 0.000001);
	EXPECT_NEAR(6.48074069, geometric_mean(6.0f, 7), 0.000001);
	EXPECT_NEAR(5.01996015, geometric_mean(6, 4.2f), 0.000001);
}

TEST(GeoMeanTest, OneIntOneDouble) {
	EXPECT_DOUBLE_EQ(2.0, geometric_mean(1, 4.0));
	EXPECT_TRUE(std::isnan(geometric_mean(1.0, -4)));
	EXPECT_NEAR(6.48074069, geometric_mean(6, 7.0), 0.00000001);
	EXPECT_NEAR(6.48074069, geometric_mean(6.0, 7), 0.00000001);
	EXPECT_NEAR(5.01996015, geometric_mean(6, 4.2), 0.00000001);
}

TEST(GeoMeanTest, TwoFloats) {
	EXPECT_DOUBLE_EQ(2.0, geometric_mean(1.0f, 4.0f));
	EXPECT_TRUE(std::isnan(geometric_mean(1.0f, -4.0f)));
	EXPECT_NEAR(6.48074069, geometric_mean(6.0f, 7.0f), 0.000001);
	EXPECT_NEAR(6.48074069, geometric_mean(6.0f, 7.0f), 0.000001);
	EXPECT_NEAR(5.01996015, geometric_mean(6.0f, 4.2f), 0.000001);
}

TEST(GeoMeanTest, TwoDoubles) {
	EXPECT_DOUBLE_EQ(2.0, geometric_mean(1.0, 4.0));
	EXPECT_TRUE(std::isnan(geometric_mean(1.0, -4.0)));
	EXPECT_NEAR(6.48074069, geometric_mean(6.0, 7.0), 0.000001);
	EXPECT_NEAR(6.48074069, geometric_mean(6.0, 7.0), 0.000001);
	EXPECT_NEAR(5.01996015, geometric_mean(6.0, 4.2), 0.000001);
}

TEST(GeoMeanTest, OneIntOneFloatOneDouble) {
	EXPECT_DOUBLE_EQ(9.0, geometric_mean(3, 9.0f, 27.0));
}

TEST(GeoMeanTest, TenInts) {
	EXPECT_DOUBLE_EQ(4.528728688116765, geometric_mean(1, 2, 3, 4, 5, 6, 7, 8, 9, 10));
}

// Intentional compile error
/*TEST(GeoMeanTest, Strings) {
	EXCEPT_TRUE(geometric_mean("a", "b"));
}*/

/*TEST(GeoMeanTest, TwentyInts) {
	EXPECT_DOUBLE_EQ(8.304361203739344, geometric_mean(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20));
}*/
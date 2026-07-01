import unittest

from solution import fizzbuzz


class TestFizzBuzz(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
            fizzbuzz(5),
            ["1", "2", "Fizz", "4", "Buzz"],
        )

    def test_fizzbuzz(self):
        self.assertEqual(fizzbuzz(15)[-1], "FizzBuzz")

    def test_all_strings(self):
        # 所有元素都应是字符串
        for x in fizzbuzz(20):
            self.assertIsInstance(x, str)


if __name__ == "__main__":
    unittest.main()

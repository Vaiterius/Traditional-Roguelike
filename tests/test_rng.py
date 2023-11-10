import unittest

from game.rng import RandomNumberGenerator

class TestRNG(unittest.TestCase):
    
    def setUp(self):
        self.seed1: str = "hello"
        self.seed2: str = "foo"

        # We can set the seed for this later on.
        # Default unseeded (current system time).
        self.rng = RandomNumberGenerator()
    
    def get_list_of_ints(self,
                         rng: RandomNumberGenerator,
                         length: int) -> list[int]:
        return [rng.random() for i in range(length)]
    
    def test_with_seed1(self):
        print("TEST SAME SEEDS")
        # Set starting seed.
        self.rng.seed = self.seed1

        random_values: list[int] = self.get_list_of_ints(self.rng, 5)
        random_values2: list[int] = self.get_list_of_ints(self.rng, 5)
        print(f"First set (seed={self.rng.seed}):")
        print(random_values)
        print(random_values2)

        # Reset seed to same seed for same initial sequence.
        self.rng.seed = self.seed1

        random_values3: list[int] = self.get_list_of_ints(self.rng, 5)
        random_values4: list[int] = self.get_list_of_ints(self.rng, 5)
        print(f"Second set (seed={self.rng.seed}):")
        print(random_values3)
        print(random_values4)

        # Compare sequences of both set of random values.
        for i in range(len(random_values)):
            self.assertEqual(random_values[i], random_values3[i])
            self.assertEqual(random_values2[i], random_values4[i])
        
        print()

    def test_different_seeds(self):
        print("TEST DIFFERENT SEEDS")
        # Set starting seed.
        self.rng.seed = self.seed1

        random_values: list[int] = self.get_list_of_ints(self.rng, 5)
        random_values2: list[int] = self.get_list_of_ints(self.rng, 5)
        print(f"First set (seed={self.rng.seed}):")
        print(random_values)
        print(random_values2)

        # Reset seed to same seed for different initial sequence.
        self.rng.seed = self.seed2

        random_values3: list[int] = self.get_list_of_ints(self.rng, 5)
        random_values4: list[int] = self.get_list_of_ints(self.rng, 5)
        print(f"Second set (seed={self.rng.seed}):")
        print(random_values3)
        print(random_values4)

        # Compare sequences of both set of random values.
        for i in range(len(random_values)):
            self.assertNotEqual(random_values[i], random_values3[i])
            self.assertNotEqual(random_values2[i], random_values4[i])
        
        print()
    
    def test_unseeded_and_seeded(self):
        print("TEST UNSEEDED WITH SEEDED")
        # Set starting seed.
        self.rng.seed = self.seed1

        random_values: list[int] = self.get_list_of_ints(self.rng, 5)
        random_values2: list[int] = self.get_list_of_ints(self.rng, 5)
        print(f"({self.rng.seed}) First set:")
        print(random_values)
        print(random_values2)

        # Reset seed to same seed for different initial sequence.
        self.rng.seed = None

        random_values3: list[int] = self.get_list_of_ints(self.rng, 5)
        random_values4: list[int] = self.get_list_of_ints(self.rng, 5)
        print(f"({self.rng.seed}) Second set:")
        print(random_values3)
        print(random_values4)

        # Compare sequences of both set of random values.
        for i in range(len(random_values)):
            self.assertNotEqual(random_values[i], random_values3[i])
            self.assertNotEqual(random_values2[i], random_values4[i])
        
        print()



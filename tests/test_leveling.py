import unittest

from game.components.leveler import Leveler, experience_needed_for_level


class TestLevelingSystem(unittest.TestCase):
    
    def setUp(self):
        self.leveler = Leveler(start_level=1, base_drop_amount=5)
    
    def print_stats(self):
        print()
        print(f"Level: {self.leveler.level}")
        print(f"XP: {self.leveler.experience}")
        print(f"XP left: {self.leveler.experience_left_to_level_up}")
        print(f"XP total: {self.leveler.total_experience}")
    
    def test_levelups(self):
        self.assertEqual(self.leveler.level, 1)
        self.assertEqual(self.leveler.experience, 0)
        self.assertEqual(self.leveler.experience_left_to_level_up, 10)
        self.assertFalse(self.leveler.can_level_up)
        
        self.leveler.absorb(5)
        self.assertEqual(self.leveler.level, 1)
        self.assertEqual(self.leveler.experience, 5)
        self.assertEqual(self.leveler.experience_left_to_level_up, 5)
        self.assertFalse(self.leveler.can_level_up)

        self.leveler.absorb(4.9)  # Should be rounded to 5.
        self.assertEqual(self.leveler.level, 1)
        self.assertEqual(self.leveler.experience, 10)
        self.assertEqual(self.leveler.experience_left_to_level_up, 0)
        self.assertTrue(self.leveler.can_level_up)

        self.print_stats()

        while self.leveler.can_level_up:
            print("CAN LEVEL UP!")
            self.leveler.level_up()
        
        self.print_stats()
        
        self.assertEqual(self.leveler.level, 2)
        self.assertEqual(self.leveler.experience, 0)
        self.assertEqual(self.leveler.total_experience, 10)
        self.assertEqual(self.leveler.experience_left_to_level_up, 15)
        self.assertFalse(self.leveler.can_level_up)

        self.leveler.absorb(23)
        while self.leveler.can_level_up:
            print("CAN LEVEL UP!")
            self.leveler.level_up()

        self.print_stats()

        self.assertEqual(self.leveler.level, 3)
        self.assertEqual(self.leveler.experience, 8)
        self.assertEqual(self.leveler.total_experience, 33)
        self.assertEqual(self.leveler.experience_left_to_level_up, 12)
        self.assertFalse(self.leveler.can_level_up)

        self.leveler

        self.leveler.absorb(123)
        self.assertTrue(self.leveler.can_level_up)
        while self.leveler.can_level_up:
            print("CAN LEVEL UP!")
            self.leveler.level_up()
        
        self.print_stats()
        
        # self.assertEqual(self.leveler.level, 3)
        # self.assertEqual(self.leveler.experience, 8)
        self.assertEqual(self.leveler.total_experience, 156)
        # self.assertEqual(self.leveler.experience_left_to_level_up, 12)
        # self.assertFalse(self.leveler.can_level_up)

    def test_experience_growth(self):
        self.assertEqual(experience_needed_for_level(2), 10)
        self.assertEqual(experience_needed_for_level(3), 15)
        self.assertEqual(experience_needed_for_level(4), 20)
        self.assertEqual(experience_needed_for_level(5), 25)
        self.assertEqual(experience_needed_for_level(6), 30)
        self.assertEqual(experience_needed_for_level(7), 35)
        self.assertEqual(experience_needed_for_level(8), 40)
        self.assertEqual(experience_needed_for_level(9), 45)
        self.assertEqual(experience_needed_for_level(10), 50)

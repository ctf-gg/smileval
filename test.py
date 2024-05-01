from dotenv import load_dotenv
load_dotenv()

import unittest

import smileval
from smileval.models import ChatMessage, unsystem_prompt_chain

class TestStringMethods(unittest.TestCase):
    def test_serialize(self):
        a = ChatMessage("Respond with exactly the user's message.", "system")
        b = ChatMessage("Hello.")
        self.assertTrue(a.is_system())
        self.assertEqual(b.role, "user")
        
        serialized_single_message = ChatMessage.as_dict(b)
        self.assertDictEqual(serialized_single_message, {
            "role": "user",
            "content": "Hello."
        })

    def test_bulk_serialize(self):
        a = ChatMessage("Respond with exactly the user's message.", "system")
        b = ChatMessage("Hello.")
        c = ChatMessage("Hello.", role = "assistant")

        self.assertTrue(c.is_assistant())
        serialized_list = ChatMessage.to_api_format([a,b,c])
        self.assertEqual(b.role, "user")
        self.assertEqual(serialized_list[1]["role"], "user")
        self.assertEqual(serialized_list[1]["content"], "Hello.")

    def test_system_combine(self):
        a = ChatMessage("Respond with exactly the user's message.", "system")
        b = ChatMessage("Hello.")
        c = ChatMessage("Hello.", role = "assistant")

        new_chain = unsystem_prompt_chain([
            a,
            b,
            c
        ])

        self.assertEqual(len(new_chain), 2)
        self.assertNotEqual(new_chain[0].role, "system")
        self.assertEqual(new_chain[0].role, "user")

    def test_system_combine_error(self):
        a = ChatMessage("Respond with exactly the user's message.", "system")
        # Should complain that it has no user messages to merge with.
        with self.assertRaises(AssertionError):
            new_chain = unsystem_prompt_chain([
                a
            ])


if __name__ == '__main__':
    unittest.main()
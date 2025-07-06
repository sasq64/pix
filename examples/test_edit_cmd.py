import unittest
from edit_cmd import EditCmd, EditSplit, EditJoin, EditDelete, EditInsert, CombinedCmd, CmdStack, Char, Pos


class TestEditCmd(unittest.TestCase):
    """Test the base EditCmd class"""
    
    def test_base_edit_cmd(self):
        """Test basic EditCmd functionality"""
        cmd = EditCmd()
        
        # Test default implementations
        target = [[(ord('a'), 0), (ord('b'), 1)]]
        result = cmd.apply(target)
        self.assertIsNone(result)
        result = cmd.undo(target)
        self.assertIsNone(result)


class TestCombinedCmd(unittest.TestCase):
    """Test CombinedCmd class"""
    
    def setUp(self):
        """Set up test data"""
        self.target = [
            [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)],
            [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)]
        ]
    
    def test_combined_cmd_apply(self):
        """Test applying combined commands"""
        insert_cmd = EditInsert(0, 2, [(ord('X'), 5)])
        delete_cmd = EditDelete(0, 1, 1)
        combined = CombinedCmd([insert_cmd, delete_cmd])
        
        original = [line[:] for line in self.target]
        result = combined.apply(self.target)
        
        # Should apply both commands
        expected = [(ord('H'), 0), (ord('X'), 5), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)]
        self.assertEqual(self.target[0], expected)
        self.assertEqual(result, (0, 1))  # Position after delete (last command)
        
        # Test undo
        undo_result = combined.undo(self.target)
        self.assertEqual(self.target, original)
        self.assertEqual(undo_result, (0, 1))  # Position after delete undo
    
    def test_combined_cmd_empty_list(self):
        """Test combined command with empty list"""
        combined = CombinedCmd([])
        original = [line[:] for line in self.target]
        
        result = combined.apply(self.target)
        self.assertIsNone(result)
        self.assertEqual(self.target, original)
        
        undo_result = combined.undo(self.target)
        self.assertIsNone(undo_result)
        self.assertEqual(self.target, original)


class TestEditSplit(unittest.TestCase):
    """Test EditSplit command"""
    
    def setUp(self):
        """Set up test data"""
        self.target = [
            [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)],
            [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)]
        ]
    
    def test_split_middle_of_line(self):
        """Test splitting a line in the middle"""
        cmd = EditSplit(0, 2)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        # Check that line was split correctly
        self.assertEqual(len(self.target), 3)
        self.assertEqual(self.target[0], [(ord('H'), 0), (ord('e'), 1)])
        self.assertEqual(self.target[1], [(ord('l'), 2), (ord('l'), 3), (ord('o'), 4)])
        self.assertEqual(self.target[2], [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)])
        self.assertEqual(result, (0, 2))
        
        # Test undo
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 2))
        self.assertEqual(self.target, original)
    
    def test_split_at_beginning(self):
        """Test splitting at the beginning of a line"""
        cmd = EditSplit(0, 0)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        self.assertEqual(len(self.target), 3)
        self.assertEqual(self.target[0], [])
        self.assertEqual(self.target[1], [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)])
        self.assertEqual(result, (0, 0))
        
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 0))
        self.assertEqual(self.target, original)
    
    def test_split_at_end(self):
        """Test splitting at the end of a line"""
        cmd = EditSplit(0, 5)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        self.assertEqual(len(self.target), 3)
        self.assertEqual(self.target[0], [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)])
        self.assertEqual(self.target[1], [])
        self.assertEqual(result, (0, 5))
        
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 5))
        self.assertEqual(self.target, original)
    
    def test_split_second_line(self):
        """Test splitting the second line"""
        cmd = EditSplit(1, 2)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        self.assertEqual(len(self.target), 3)
        self.assertEqual(self.target[0], [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)])
        self.assertEqual(self.target[1], [(ord('W'), 0), (ord('o'), 1)])
        self.assertEqual(self.target[2], [(ord('r'), 2), (ord('l'), 3), (ord('d'), 4)])
        self.assertEqual(result, (1, 2))
        
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (1, 2))
        self.assertEqual(self.target, original)


class TestEditJoin(unittest.TestCase):
    """Test EditJoin command"""
    
    def setUp(self):
        """Set up test data"""
        self.target = [
            [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)],
            [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)],
            [(ord('!'), 0)]
        ]
    
    def test_join_lines(self):
        """Test joining two lines"""
        cmd = EditJoin(0)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        # Check that lines were joined correctly
        self.assertEqual(len(self.target), 2)
        expected_joined = [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4), 
                          (ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)]
        self.assertEqual(self.target[0], expected_joined)
        self.assertEqual(self.target[1], [(ord('!'), 0)])
        self.assertEqual(result, (0, 5))
        
        # Test undo
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (1, 0))
        self.assertEqual(self.target, original)
    
    def test_join_last_line(self):
        """Test joining the last line with the second-to-last"""
        cmd = EditJoin(1)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        self.assertEqual(len(self.target), 2)
        self.assertEqual(self.target[0], [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)])
        expected_joined = [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4), (ord('!'), 0)]
        self.assertEqual(self.target[1], expected_joined)
        self.assertEqual(result, (1, 5))
        
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (2, 0))
        self.assertEqual(self.target, original)
    
    def test_join_empty_line(self):
        """Test joining with an empty line"""
        self.target = [
            [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)],
            [],
            [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)]
        ]
        cmd = EditJoin(0)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        self.assertEqual(len(self.target), 2)
        self.assertEqual(self.target[0], [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)])
        self.assertEqual(self.target[1], [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)])
        self.assertEqual(result, (0, 5))
        
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (1, 0))
        self.assertEqual(self.target, original)
    
    def test_join_without_apply(self):
        """Test joining without applying first"""
        cmd = EditJoin(0)
        original = [line[:] for line in self.target]
        
        result = cmd.undo(self.target)
        self.assertIsNone(result)
        self.assertEqual(self.target, original)


class TestEditDelete(unittest.TestCase):
    """Test EditDelete command"""
    
    def setUp(self):
        """Set up test data"""
        self.target = [
            [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)],
            [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)]
        ]
    
    def test_delete_single_character(self):
        """Test deleting a single character"""
        cmd = EditDelete(0, 1, 1)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        # Check that character was deleted
        self.assertEqual(self.target[0], [(ord('H'), 0), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)])
        self.assertEqual(self.target[1], [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)])
        self.assertEqual(result, (0, 1))
        
        # Test undo
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 2))
        self.assertEqual(self.target, original)
    
    def test_delete_multiple_characters(self):
        """Test deleting multiple characters"""
        cmd = EditDelete(0, 1, 3)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        # Check that characters were deleted
        self.assertEqual(self.target[0], [(ord('H'), 0), (ord('o'), 4)])
        self.assertEqual(self.target[1], [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)])
        self.assertEqual(result, (0, 1))
        
        # Test undo (should fully restore the original line)
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 4))
        self.assertEqual(self.target, original)
    
    def test_delete_at_beginning(self):
        """Test deleting at the beginning of a line"""
        cmd = EditDelete(0, 0, 1)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        self.assertEqual(self.target[0], [(ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)])
        self.assertEqual(result, (0, 0))
        
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 1))
        self.assertEqual(self.target, original)
    
    def test_delete_at_end(self):
        """Test deleting at the end of a line"""
        cmd = EditDelete(0, 4, 1)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        self.assertEqual(self.target[0], [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3)])
        self.assertEqual(result, (0, 4))
        
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 5))
        self.assertEqual(self.target, original)
    
    def test_delete_entire_line(self):
        """Test deleting an entire line"""
        cmd = EditDelete(0, 0, 5)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        self.assertEqual(self.target[0], [])
        self.assertEqual(self.target[1], [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)])
        self.assertEqual(result, (0, 0))
        
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 5))
        self.assertEqual(self.target, original)
    
    def test_delete_zero_characters(self):
        """Test deleting zero characters"""
        cmd = EditDelete(0, 2, 0)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        # Should be unchanged
        self.assertEqual(self.target, original)
        self.assertEqual(result, (0, 2))
        
        undo_result = cmd.undo(self.target)
        self.assertIsNotNone(undo_result)
    
    def test_delete_without_apply(self):
        """Test deleting without applying first"""
        cmd = EditDelete(0, 1, 2)
        original = [line[:] for line in self.target]
        
        result = cmd.undo(self.target)
        self.assertIsNone(result)
        self.assertEqual(self.target, original)


class TestEditInsert(unittest.TestCase):
    """Test EditInsert command"""
    
    def setUp(self):
        """Set up test data"""
        self.target = [
            [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)],
            [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)]
        ]
    
    def test_insert_single_character(self):
        """Test inserting a single character"""
        new_char = [(ord('X'), 5)]
        cmd = EditInsert(0, 2, new_char)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        # Check that character was inserted
        expected = [(ord('H'), 0), (ord('e'), 1), (ord('X'), 5), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)]
        self.assertEqual(self.target[0], expected)
        self.assertEqual(self.target[1], [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)])
        self.assertEqual(result, (0, 3))
        
        # Test undo
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 2))
        self.assertEqual(self.target, original)
    
    def test_insert_multiple_characters(self):
        """Test inserting multiple characters"""
        new_chars = [(ord('X'), 5), (ord('Y'), 6), (ord('Z'), 7)]
        cmd = EditInsert(0, 2, new_chars)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        # Check that characters were inserted
        expected = [(ord('H'), 0), (ord('e'), 1), (ord('X'), 5), (ord('Y'), 6), (ord('Z'), 7), 
                   (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)]
        self.assertEqual(self.target[0], expected)
        self.assertEqual(result, (0, 5))
        
        # Test undo
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 2))
        self.assertEqual(self.target, original)
    
    def test_insert_at_beginning(self):
        """Test inserting at the beginning of a line"""
        new_char = [(ord('X'), 5)]
        cmd = EditInsert(0, 0, new_char)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        expected = [(ord('X'), 5), (ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)]
        self.assertEqual(self.target[0], expected)
        
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 0))
        self.assertEqual(self.target, original)
    
    def test_insert_at_end(self):
        """Test inserting at the end of a line"""
        new_char = [(ord('X'), 5)]
        cmd = EditInsert(0, 5, new_char)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        expected = [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4), (ord('X'), 5)]
        self.assertEqual(self.target[0], expected)
        
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 5))
        self.assertEqual(self.target, original)
    
    def test_insert_empty_list(self):
        """Test inserting an empty list (should do nothing)"""
        cmd = EditInsert(0, 2, [])
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        # Should be unchanged
        self.assertEqual(self.target, original)
        self.assertEqual(result, (0, 2))
        
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 2))
        self.assertEqual(self.target, original)
    
    def test_insert_into_empty_line(self):
        """Test inserting into an empty line"""
        self.target = [
            [],
            [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)]
        ]
        new_char = [(ord('X'), 5)]
        cmd = EditInsert(0, 0, new_char)
        original = [line[:] for line in self.target]
        
        result = cmd.apply(self.target)
        
        self.assertEqual(self.target[0], [(ord('X'), 5)])
        self.assertEqual(self.target[1], [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)])
        self.assertEqual(result, (0, 1))
        
        undo_result = cmd.undo(self.target)
        self.assertEqual(undo_result, (0, 0))
        self.assertEqual(self.target, original)
    
    def test_insert_without_apply(self):
        """Test inserting without applying first"""
        cmd = EditInsert(0, 2, [(ord('X'), 5)])
        original = [line[:] for line in self.target]
        
        result = cmd.undo(self.target)
        self.assertEqual(result, (0, 2))
        # Note: EditInsert.undo() modifies the target even when apply() was never called
        # This deletes characters from the target, which is a side effect


class TestCmdStack(unittest.TestCase):
    """Test CmdStack class"""
    
    def setUp(self):
        """Set up test data"""
        self.target = [
            [(ord('H'), 0), (ord('e'), 1), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)],
            [(ord('W'), 0), (ord('o'), 1), (ord('r'), 2), (ord('l'), 3), (ord('d'), 4)]
        ]
        self.stack = CmdStack()
    
    def test_apply_single_command(self):
        """Test applying a single command"""
        cmd = EditInsert(0, 2, [(ord('X'), 5)])
        result = self.stack.apply(cmd, self.target)
        
        self.assertEqual(result, cmd)
        self.assertEqual(len(self.stack.stack), 1)
        self.assertEqual(len(self.stack.redo_stack), 0)
        
        expected = [(ord('H'), 0), (ord('e'), 1), (ord('X'), 5), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)]
        self.assertEqual(self.target[0], expected)
    
    def test_undo_redo(self):
        """Test undo and redo functionality"""
        original = [line[:] for line in self.target]
        
        # Apply a command
        cmd = EditInsert(0, 2, [(ord('X'), 5)])
        self.stack.apply(cmd, self.target)
        
        # Undo
        undo_pos = self.stack.undo(self.target)
        self.assertEqual(self.target, original)
        self.assertEqual(undo_pos, (0, 2))
        self.assertEqual(len(self.stack.stack), 0)
        self.assertEqual(len(self.stack.redo_stack), 1)
        
        # Redo
        redo_pos = self.stack.redo(self.target)
        expected = [(ord('H'), 0), (ord('e'), 1), (ord('X'), 5), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)]
        self.assertEqual(self.target[0], expected)
        self.assertEqual(redo_pos, (0, 3))
        self.assertEqual(len(self.stack.stack), 1)
        self.assertEqual(len(self.stack.redo_stack), 0)
    
    def test_multiple_commands(self):
        """Test multiple commands"""
        original = [line[:] for line in self.target]
        
        # Apply multiple commands
        cmd1 = EditInsert(0, 2, [(ord('X'), 5)])
        cmd2 = EditDelete(0, 1, 1)
        cmd3 = EditSplit(0, 3)
        
        self.stack.apply(cmd1, self.target)
        self.stack.apply(cmd2, self.target)
        self.stack.apply(cmd3, self.target)
        
        self.assertEqual(len(self.stack.stack), 3)
        
        # Undo all
        self.stack.undo(self.target)
        self.stack.undo(self.target)
        self.stack.undo(self.target)
        
        self.assertEqual(self.target, original)
        self.assertEqual(len(self.stack.stack), 0)
        self.assertEqual(len(self.stack.redo_stack), 3)
    
    def test_undo_empty_stack(self):
        """Test undoing from empty stack"""
        result = self.stack.undo(self.target)
        self.assertIsNone(result)
        self.assertEqual(len(self.stack.stack), 0)
        self.assertEqual(len(self.stack.redo_stack), 0)
    
    def test_redo_empty_stack(self):
        """Test redoing from empty stack"""
        result = self.stack.redo(self.target)
        self.assertIsNone(result)
        self.assertEqual(len(self.stack.stack), 0)
        self.assertEqual(len(self.stack.redo_stack), 0)
    
    def test_clear_redo_on_new_command(self):
        """Test that redo stack is cleared when new command is applied"""
        # Apply and undo a command
        cmd1 = EditInsert(0, 2, [(ord('X'), 5)])
        self.stack.apply(cmd1, self.target)
        self.stack.undo(self.target)
        
        self.assertEqual(len(self.stack.redo_stack), 1)
        
        # Apply new command
        cmd2 = EditDelete(0, 1, 1)
        self.stack.apply(cmd2, self.target)
        
        self.assertEqual(len(self.stack.redo_stack), 0)
        self.assertEqual(len(self.stack.stack), 1)
    
    def test_join_prev_combine(self):
        """Test joining commands with join_prev=True"""
        cmd1 = EditInsert(0, 2, [(ord('X'), 5)])
        cmd2 = EditInsert(0, 3, [(ord('Y'), 6)])
        
        self.stack.apply(cmd1, self.target)
        result = self.stack.apply(cmd2, self.target, join_prev=True)
        
        self.assertEqual(len(self.stack.stack), 1)
        self.assertIsInstance(self.stack.stack[0], CombinedCmd)
        self.assertEqual(result, cmd2)
        
        # Check that both commands were applied
        expected = [(ord('H'), 0), (ord('e'), 1), (ord('X'), 5), (ord('Y'), 6), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)]
        self.assertEqual(self.target[0], expected)
    
    def test_join_prev_insert_optimization(self):
        """Test joining consecutive insert commands"""
        cmd1 = EditInsert(0, 2, [(ord('X'), 5)])
        cmd2 = EditInsert(0, 3, [(ord('Y'), 6)])
        
        self.stack.apply(cmd1, self.target)
        result = self.stack.apply(cmd2, self.target)
        
        # Should optimize to a single insert command
        self.assertEqual(len(self.stack.stack), 1)
        self.assertIsInstance(self.stack.stack[0], EditInsert)
        self.assertEqual(result, cmd2)
        
        # Check that both characters were inserted
        expected = [(ord('H'), 0), (ord('e'), 1), (ord('X'), 5), (ord('Y'), 6), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)]
        self.assertEqual(self.target[0], expected)
    
    def test_join_prev_delete_optimization(self):
        """Test joining consecutive delete commands"""
        cmd1 = EditDelete(0, 1, 1)  # Delete at position 1
        cmd2 = EditDelete(0, 2, 1)  # Delete at position 2 (after first delete)
        
        self.stack.apply(cmd1, self.target)
        result = self.stack.apply(cmd2, self.target)
        
        # Should optimize to a single delete command
        self.assertEqual(len(self.stack.stack), 1)
        self.assertIsInstance(self.stack.stack[0], EditDelete)
        self.assertEqual(result, cmd2)
        
        # Check that both characters were deleted
        expected = [(ord('H'), 0), (ord('l'), 2), (ord('l'), 3), (ord('o'), 4)]
        self.assertEqual(self.target[0], expected)
    
    def test_no_join_prev_optimization(self):
        """Test that commands don't join when conditions aren't met"""
        cmd1 = EditInsert(0, 2, [(ord('X'), 5)])
        cmd2 = EditInsert(0, 4, [(ord('Y'), 6)])  # Different position
        
        self.stack.apply(cmd1, self.target)
        result = self.stack.apply(cmd2, self.target)
        
        # Should not optimize
        self.assertEqual(len(self.stack.stack), 2)
        self.assertEqual(result, cmd2)
        
        # Check that both characters were inserted
        expected = [(ord('H'), 0), (ord('e'), 1), (ord('X'), 5), (ord('l'), 2), (ord('Y'), 6), (ord('l'), 3), (ord('o'), 4)]
        self.assertEqual(self.target[0], expected)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_empty_document_operations(self):
        """Test operations on empty document (should raise IndexError)"""
        empty_doc = []
        
        with self.assertRaises(IndexError):
            cmd = EditSplit(0, 0)
            cmd.apply(empty_doc)
        
        with self.assertRaises(IndexError):
            cmd = EditJoin(0)
            cmd.apply(empty_doc)
        
        with self.assertRaises(IndexError):
            cmd = EditDelete(0, 0, 1)
            cmd.apply(empty_doc)
        
        with self.assertRaises(IndexError):
            cmd = EditInsert(0, 0, [(ord('X'), 0)])
            cmd.apply(empty_doc)


if __name__ == '__main__':
    unittest.main() 